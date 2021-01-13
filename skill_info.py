from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import json
import pandas as pd
import time


def skill_info(skill_URL, web_driver):
    """ Function fetches skill description from a given skill URL

    Arg: 
            skill_URL (str) : The URL of the skill of interest
            driver (webdriver) : The webdriver object for page retrieval


    Return: 
            text containing description of input URL/skill
    """
    web_driver.get(skill_URL)
    description = web_driver.find_element_by_id('a2s-description')
    desc_text = description.text
    desc_text = desc_text.replace("\n", " ").replace("  ", " ")
    desc_text = desc_text.partition(" ")[2]
    return desc_text


def authHateBase(payload, auth_endpoint):
    """ Function returns authentication token """
    response = requests.request("POST", auth_endpoint, data=payload)
    token = response.json()["result"]["token"]
    return token


def analyseSkill(payload, analysis_endpoint):
    """ Function returns request_id for query to the Hatebase '/analyze' endpoint """
    response = requests.request("POST", analysis_endpoint, data=payload)
    request_id = response.json()["result"]["request_id"]
    return request_id


def getAnalysisResponse(payload, get_analysis_endpoint):
    """ Function returns result of query analysis """
    response = requests.request("POST", get_analysis_endpoint, data=payload)
    result = response.json()["result"]
    return(result)


def main():
    # Set up the webdriver for crawling text from a skill url
    options = Options()
    options.headless = True
    # path to chrome driver
    DRIVER_PATH = r'C:/Program Files (x86)/Google/Chrome/Application/chromedriver.exe'
    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
    # replace "AMAZON SKILL URL" with url to interested skill
    page_URL = "AMAZON SKILL URL"
    skill_text = skill_info(page_URL, driver)
    print('SKILL DESCRIPTION \n {}'.format(skill_text))

    # Authenticate to the HateBase API and obtain a token (one hour expiration period)
    auth_url = "https://api.hatebase.org/4-4/authenticate"
    # Replace '************' with your api_key
    auth_payload = {'api_key': '************'}
    auth_token = authHateBase(auth_payload, auth_url)
    print('\n AUTHENTICATION TOKEN \n {}'.format(auth_token))

    # Request analysis of skill description and obtain request id
    # set analyze endpoint variable
    analysis_url = "https://api.hatebase.org/4-4/analyze"
    # Initialize payload (request) format, language, country, and search option
    text_format = 'json'
    lang = 'ENG'
    country = 'UK'
    search_option = 'false'
    # Create analysis payload for /analyze endpoint
    analysis_payload = {'token': auth_token,
                        'format': text_format,
                        'content': skill_text,
                        'language': lang,
                        'country': country,
                        'broadest_possible_search': search_option}
    analysis_id = analyseSkill(analysis_payload, analysis_url)
    print('\n ANALYSIS REQUEST ID \n {}'.format(analysis_id))

    # Get result of analysis using id output from analyze request
    get_analysis_url = "https://api.hatebase.org/4-4/get_analysis"
    get_payload = {'token': auth_token,
                   'format': text_format,
                   'request_id': analysis_id}
    # wait 60 seconds for analysis result before querying HateBase for result
    time.sleep(60)
    analysis_result = getAnalysisResponse(get_payload, get_analysis_url)
    print('\n ANALYSIS RESULT \n {}'.format(analysis_result))


if __name__ == '__main__':
    main()
