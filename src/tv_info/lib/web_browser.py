from selenium import webdriver


class WebBrowser:
    def __init__(self, opts: dict = None):
        self.opts = opts or {}
        self.driver = None  # type: webdriver.Chrome

    def __enter__(self):
        self.driver = self.create_driver()
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()

    def create_driver(self):
        options = webdriver.ChromeOptions()
        options.headless = self.opts.get("headless", True)
        if self.opts.get("no-sandbox"):
            options.add_argument('--no-sandbox')
        if self.opts.get("user_agent"):
            options.add_argument("user-agent=%(user_agent)s" % self.opts)
        desired_capabilities = {"acceptInsecureCerts": self.opts.get("acceptInsecureCerts", True)}
        return webdriver.Chrome(options=options, desired_capabilities=desired_capabilities)
