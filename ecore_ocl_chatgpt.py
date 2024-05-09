import openai
import itertools
import subprocess
import penenadpi_file_utilities as utilities

CHATGPT_KEY = "YOUR_OPENAI_KEY"

class PromptManager:
  def __init__(self):
    self.prompt1 =  "According to PAR_1 generate Ecore model instance based on given metamodel PAR_2"
    self.prompt2 =  "According to PAR_1 generate OCL constraints based on given metamodel PAR_2"
    self.prompt3 = "Parametrize experiment based on template PAR_1 using model instance PAR_2"

  def fillTemplate(self, params, template):
    count = 1
    filled = template
    for par in params:
      tmp = "PAR_"+ str(count)
      filled = filled.replace(tmp, par)
      count = count + 1
    return filled

  def fillFirstTemplate(self, params: list):
    return self.fillTemplate(params, self.prompt1)

  def fillSecondTemplate(self, params: list):
    return self.fillTemplate(params, self.prompt2)

  def fillThirdTemplate(self, params: list):
    return self.fillTemplate(params, self.prompt3)


class ChatGptInterface:
  def __init__(self, apiKey):
    self.__api_key =  apiKey

  def setApiKey(self, apiKey):
    self.__api_key = apiKey

  def executePrompt(self, prompt, model="gpt-3.5-turbo"):
    openai.api_key = self.__api_key

    messages = [{"role": "user", "content": prompt}]

    response = openai.ChatCompletion.create(

    model=model,

    messages=messages,

    temperature=0,

    )

    return response.choices[0].message["content"]

class Generator:

  def __init__(self, apiKey):
    self.pm = PromptManager()
    self.gpt = ChatGptInterface(apiKey)
    self.ut = Utilities()

  def generateExperimentModel(self, description):
    prompt = self.pm.fillFirstTemplate([description, self.ut.fileToString("network_exp_metamodel.ecore")])
    res = self.gpt.executePrompt(prompt)
    self.ut.stringToFile("experiment1.xmi", res)
    return res

  def generateExperiment(self, templatePath, experimentModelPath):
    prompt = self.pm.fillThirdTemplate([self.ut.fileToString(templatePath), self.ut.fileToString(experimentModelPath)])
    res = self.gpt.executePrompt(prompt)
    self.ut.stringToFile("experiment1.txt", res)
    return res


class ModelVerificator:
  def __init__(self):
    pass

  def verifyModel(self, metamodelPath, instancePath, rulesPath):
    subprocess.call(['java', '-jar', 'checker.jar', metamodelPath, rulesPath, instancePath])


generator = Generator(CHATGPT_KEY)
generator.generateExperimentModel("Beaulieu-Xie fading κappa-mi CCI, diversity combining outage probability 1 receiver")
generator.generateConstraints("Deployment should have at least two base stations")
verificator = ModelVerificator()
verificator.verifyModel("network_exp_metamodel.ecore", "experiment1.xmi", "rules1.ocl")
generator.generateExperiment("experiment_template.txt", "experiment1.xmi")
