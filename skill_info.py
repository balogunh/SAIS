from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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

def main():

	options = Options()
	options.headless = True

	DRIVER_PATH = r'C:/Program Files (x86)/Google/Chrome/Application/chromedriver.exe'
	driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
	page_URL = "https://www.amazon.com/gp/product/B08NR9YN13?ref=skillrw_dsk_editorspicks__0" 
	skill_text = skill_info(page_URL, driver)
	
	print(skill_text)


if __name__ == '__main__':
	main()
