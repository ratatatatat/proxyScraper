import csv
import string
import urllib2
from bs4 import BeautifulSoup
import json
import sys
import re
import cssutils

class ProxyFinder():
	def __init__(self):
		self.proxyList = self.getProxies()
		# print self.proxyList

	def getFastestProxies(self):
		return self.sortProxyByKey('speed',False)

	def getFastestConnProxies(self):
		return self.sortProxyByKey('connTime')

	def sortProxyByKey(self,key,bAscending = True):
		retArray = self.proxyList
		for i in range(len(retArray)):
			bContinue = False
			for x in range( len(retArray) - 1):
				if(bAscending):
					if(float(retArray[x][key]) < float(retArray[x + 1][key])):
						tempFor = retArray [x + 1]
						tempCur = retArray[x] 
						retArray[x] = tempFor
						retArray[x + 1] = tempCur
						bContinue = True
					else:
						continue
				else:
					if(float(retArray[x][key]) > float(retArray[x + 1][key])):
						tempFor = retArray [x + 1]
						tempCur = retArray[x] 
						retArray[x] = tempFor
						retArray[x + 1] = tempCur
						bContinue = True
					else:
						continue					
			if(bContinue):
				continue
			else:
				break
		return retArray

	def getProxies(self):
		proxySource  = 'http://proxylist.hidemyass.com/'
		htmlObj = self.getHtml(proxySource)
		proxyList = []
		if(htmlObj['status'] == 'success'):
			htmlText = htmlObj['payload']
			soup = BeautifulSoup(htmlText,'html.parser')
			table = soup.find('table', id='listable')
			tableBody = table.tbody
			rows = tableBody.find_all('tr')
			# Each row represents a proxy obj
			for row in rows:
				proxyObj = {}
				cols = row.find_all('td')
				for index,col in enumerate(cols):
					if(index == 0):
						proxyObj['updateTime'] = col.get_text().strip()
					elif(index == 1):
						proxyObj['ip'] = self.extractIP(col)
					elif(index == 2):
						proxyObj['port'] = col.get_text().strip()
					elif(index == 3):
						proxyObj['country'] = col.get_text().strip()
					elif(index == 4):
						proxyObj['speed'] = col.div['value']
					elif(index == 5):
						proxyObj['connTime'] = col.div['value']
					elif(index == 6):
						proxyObj['protocol'] = col.get_text().strip().lower()
					elif(index == 7):
						proxyObj['anon'] = col.get_text().strip()
					else:
						continue
				proxyList.append(proxyObj)
		return proxyList

	def isVisibleElement(self,element,styleSheet):
		print styleSheet
		if('class' in element.attrs):
			className = element['class'][0]
			# print className
			try:
				return styleSheet[className]
			except:
				return True
		else:
			if('style' in element.attrs):
				styleValue = element['style']
				if('none' in styleValue):
					return False
				else:
					return True
			else:
				return True

	def extractIP(self,col):
		IP=''
		print col.span.get_text()
		children = col.span.findChildren()
		styleSheet = self.extractStyle(col)
		for child in children:
			# print child.get_text()
			if(child.name == 'style'):
				child.decompose()
				continue
			else:
				if(self.isVisibleElement(child,styleSheet)):
					continue
				else:
					child.decompose()
					continue
		return col.span.get_text().strip()



	def extractStyle(self,col):
		styles = col.span.style.get_text()
		cssSheet = cssutils.parseString(styles)
		styleSheet = {}
		for rule in cssSheet:
			className = rule.selectorText.replace('.','')
			classValue = rule.style.cssText
			if('none' in classValue.lower()):
				styleSheet[className] = False
			else:
				styleSheet[className] = True
			continue
		print styleSheet
		return styleSheet		

	# returns the HTML of the page
	def getHtml(self,url):
		returnObj = {}
		try:
			headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
			req = urllib2.Request(url, None, headers)
			htmlText = urllib2.urlopen(req,timeout=10).read()
			returnObj['status'] = 'success'
			returnObj['payload'] = htmlText
			return returnObj
		except:
			e = sys.exc_info()[0]
			returnObj['status'] = 'failure'
			returnObj['payload'] = None
			return returnObj

def main():
	p = ProxyFinder()
	sortedList = p.getFastestProxies()
	for proxy in sortedList:
		print proxy

if __name__ == '__main__':
	main()