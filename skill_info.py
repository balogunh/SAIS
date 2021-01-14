from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import json
import pandas as pd
import time
from collections import OrderedDict

def skillDesc(skill_URL, web_driver):
    """ Function returns text containing description of input URL skill
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

def dataPreprocessing(path_to_data, driver):
	""" Function returns dict of skill name and description """
	result_dict = {}
	df = pd.read_csv(path_to_data, usecols=[0,1], header=0)
	dict_Skills = dict(df.values.tolist())
	for key,value in dict_Skills.items():
		page_URL = value
		skill_text = skillDesc(page_URL, driver)
		result_dict[key] = skill_text
	return result_dict


def main():
    # Set up the webdriver for crawling text from a skill url
    options = Options()
    options.headless = True
    # Replace path to chrome driver with your chromediver path
    DRIVER_PATH = 'chromedriver/path'
    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

    #Generate for skill and descriptions csv from url csv file
    path_to_data = "data/inputData.csv"
    desc_dict = dataPreprocessing(path_to_data, driver)
    pd_result = pd.DataFrame.from_dict(data=desc_dict, orient='index', columns=['Skill Description'])
    pd_result.to_csv('data/skillDescription.csv')

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
    country = 'GB'
    search_option = 'false'
    analysis_id_list = []

    # Create analysis payloads for /analyze endpoint
    desc_dict = OrderedDict(desc_dict)
    for skill_text in desc_dict.values():

	    analysis_payload = {'token': auth_token,
	                        'format': text_format,
	                        'content': skill_text,
	                        'language': lang,
	                        'country': country,
	                        'broadest_possible_search': search_option}
	    analysis_id = analyseSkill(analysis_payload, analysis_url)
	    analysis_id_list.append(analysis_id)
	    # print('\n ANALYSIS REQUEST ID \n {}'.format(analysis_id))
    print('\n ANALYSIS REQUEST ID LIST \n {}'.format(analysis_id_list))

    # Get result of analysis using id output (analysis_id_list) from analyze requests
    res_analysis_url = "https://api.hatebase.org/4-4/get_analysis"
    res_payload = {'token': auth_token,
                   'format': text_format,
                   'request_id': analysis_id_list[0]}
    # # wait for sometime for HateBase API to generate result seconds for analysis result before querying HateBase for result
    time.sleep(120)
    analysis_result = getAnalysisResponse(res_payload, res_analysis_url)
    print('\n ANALYSIS RESULT \n {}'.format(analysis_result))
    # Create initial dataframe from first result
    res_df = pd.DataFrame(data=analysis_result, index=[0])

    # Append results of other queries to dataframe
    for query_id in range(1, len(analysis_id_list)):
    	res_payload = {'token': auth_token,
                   'format': text_format,
                   'request_id': analysis_id_list[query_id]}
    	analysis_result = getAnalysisResponse(res_payload, res_analysis_url)
    	res_df =res_df.append(analysis_result, ignore_index=True)

    res_df.reset_index(drop=True, inplace=True)
    res_df.to_csv("data/hateBaseQueryResult.csv")


    #TODO:
    #		automated url scraping for all skills
    #		Write data to csv
    #		run query against scraped skills




if __name__ == '__main__':
    main()
