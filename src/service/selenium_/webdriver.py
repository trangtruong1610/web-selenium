from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from src.service.selenium_.window_size import WindowSize

IMPLICIT_WAIT = 3
WebDriverWait_TIMEOUT = IMPLICIT_WAIT


##region webdriver loading
def loadWebDriver(remoteHub, windowSize=WindowSize.PC):
    driver = loadWebDriver_remote(remoteHub, windowSize)
    return driver


def loadWebDriver_remote(remoteHub, windowSize):
    driver = webdriver.Remote(
        command_executor=remoteHub,
        desired_capabilities=DesiredCapabilities.CHROME, #TODO also support windowSize, implicitWait - how?
    )
    return driver


def loadWebDriver_localCHROME(windowSize=WindowSize.PC, implicitWait=IMPLICIT_WAIT):

    ##region webdriver option

    #create options that be passed to the WebDriver initializer
    options = webdriver.ChromeOptions()

    #tell selenium to use the beta/dev channel version of chrome
    options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' #for MacOS
    #options.binary_location = '/usr/bin/google-chrome-beta' #for linux

    #set headless mode for chrome
    options.add_argument('headless')


    #region set the window size
    if windowSize == WindowSize.MAXIMIZED:
        #set Chrome window maximize ref. https://stackoverflow.com/a/12213723/248616 #TODO Why size 800x600 not full?
        options.add_argument("--start-maximized")
    else:
        options.add_argument('window-size=%s' % windowSize)
    #endregion set the window size


    #more options go here ref. https://sites.google.com/a/chromium.org/chromedriver/capabilities

    ##endregion webdriver option


    #initialize the driver
    driver = webdriver.Chrome(chrome_options=options)  #If nothing happens then everything worked! Normally, a new browser window would pop open at this point with a warning about being controlled by automated test software. It not appearing is exactly what we want to happen in headless mode and it means that we could be running our code on a server that doesn't even have a graphical environment. Everything from here on out is just standard Selenium so if you were only trying to figure out how to get it working with Chrome in headless mode then that's it!

    #config the implicit wait aka. default waiting time for any action ref. http://www.seleniumhq.org/docs/04_webdriver_advanced.jsp#implicit-waits
    driver.implicitly_wait(implicitWait) #in seconds

    return driver


def loadWebDriver_localFIREFOX(windowSize=WindowSize.PC_dict, implicitWait=IMPLICIT_WAIT):
    """
    ref. http://www.seleniumhq.org/docs/03_webdriver.jsp#firefox-driver
    ref. https://github.com/SeleniumHQ/selenium/wiki/FirefoxDriver
    """

    #initialize the driver
    profile = webdriver.FirefoxProfile()
    profile.native_events_enabled = True

    #NOTE we DON'T need to specify firefox binary path
    #profile.set_preference('webdriver.firefox.bin', '/usr/bin/firefox') #ref. https://github.com/SeleniumHQ/selenium/wiki/FirefoxDriver#important-system-properties

    driver = webdriver.Firefox(profile)

    #set window size
    driver.set_window_position(0, 0)
    driver.set_window_size(windowSize['width'], windowSize['height'])

    #config the implicit wait aka. default waiting time for any action ref. http://www.seleniumhq.org/docs/04_webdriver_advanced.jsp#implicit-waits
    driver.implicitly_wait(implicitWait) #in seconds

    return driver
##endregion webdriver loading


##region webdriver movement shortcut

#send_keys via action (we want to 'move to element' first)
def sendKey(driver, element, keys):
    actions = webdriver.ActionChains(driver)
    actions.move_to_element(element)
    actions.click()
    actions.send_keys(keys)
    actions.perform()


#click an element <= move to it first
def click(driver, element):
    actions = webdriver.ActionChains(driver)
    actions.move_to_element(element)
    actions.click()
    actions.perform()


#move to an element
def moveTo(driver, element):
    #code 00 ref. https://stackoverflow.com/a/41744403/248616
    driver.execute_script("arguments[0].scrollIntoView();", element)

    #code 01
    actions = webdriver.ActionChains(driver)
    actions.move_to_element(element)
    actions.perform()


#click ok/accept to close the jg alert() box
def acceptAlert(driver):
    try:
        driver.switch_to_alert().accept() #TODO better not use switch_to_alert(), why? ref. https://stackoverflow.com/questions/30146259/how-to-handle-javascript-alerts-in-selenium-using-python#comment77422039_30146662
    except:
        pass #TODO Why sometimes the alert() box not exists?


#region visibility
"""
TODO consider to use lambda ref. https://seleniumhq.github.io/selenium/docs/api/py/webdriver_support/selenium.webdriver.support.wait.html#module-selenium.webdriver.support.wait
element = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_id("someId"))
is_disappeared = WebDriverWait(driver, 30, 1, (ElementNotVisibleException)).until_not(lambda x: x.find_element_by_id(“someId”).is_displayed())
"""

def wait4VisibleCSS(driver, cssSelector):
    """given a css selector, we will 1) get the element, 2) move/scroll to it, 3) ensure it is visible"""
    from .webdriverwait import wdw, By, EC

    #get the element
    # element = wdw(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, cssSelector))) #TODO why this sometimes not working
    element = wdw(driver).until(lambda wd: wd.find_element_by_css_selector(cssSelector))

    #move to it if possible; exception raised if cannot
    moveTo(driver, element)

    #ensure visibility
    #element = wdw(driver).until(EC.visibility_of_element_located((By.CSS_SELECTOR, cssSelector)))
    wdw(driver).until(lambda wd: wd.find_element_by_css_selector(cssSelector).is_displayed())

    return element

def wait4VisibleXPath(driver, xpath, moveToIt=True):
    """given a css xpath, we will 1) get the element, 2) move/scroll to it, 3) ensure it is visible"""

    from .webdriverwait import wdw, By, EC

    #get the element
    # element = wdw(driver).until(EC.presence_of_element_located((By.XPATH, xpath))) #TODO why this sometimes not working
    element = wdw(driver).until(lambda wd: wd.find_element_by_xpath(xpath))

    #move to it if possible; exception raised if cannot
    if moveToIt: moveTo(driver, element)

    #ensure visibility
    #element = wdw(driver).until(EC.visibility_of_element_located((By.XPATH, xpath))) #TODO why cannot run this code
    #wdw(driver).until(lambda wd: wd.find_element_by_xpath(xpath).is_displayed())     #TODO why cannot run this code

    return element

def wait4InvisibleXPath(driver, xpath):
    """given an xpath selector, we will wait until it is invisible"""
    from .webdriverwait import wdw, By, EC
    wdw(driver).until_not(lambda wd: wd.find_element_by_xpath(xpath).is_displayed())

#endregion visibility

##endregion webdriver movement shortcut
