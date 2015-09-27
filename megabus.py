from selenium import webdriver
import time
import string
import datetime

def createSearchString(departDate, returnDate):
	departDate = departDate.split('-')
	returnDate = returnDate.split('-')
	outboundString = (departDate[0] + "%2f" + departDate[1] + "%2f" + departDate[2])
	inboundString = (returnDate[0] + '%2f' + returnDate[1] + '%2f' + returnDate[2])
	url1 = 'http://ca.megabus.com/JourneyResults.aspx?originCode=145&destinationCode=276&outboundDepartureDate='
	url2 = '&inboundDepartureDate='
	url3 = '&passengerCount=1&transportType=0&concessionCount=0&nusCount=0&outboundWheelchairSeated=0&outboundOtherDisabilityCount=0'
	url4 = '&inboundWheelchairSeated=0&inboundOtherDisabilityCount=0&outboundPcaCount=0&inboundPcaCount=0&promotionCode=&withReturn=1'
	searchString = url1 + outboundString + url2 + inboundString + url3 + url4
	return searchString

def isolateItems(textString, date):
	res = textString.find('Reserved')
	split = textString.split('\n')
	depart = split[0]
	departTime = depart[8:13]
	arrive = split[1]
	arriveTime = arrive[8:13]
	if res != -1:
		price = split[5]
		priceValue = price[6:10]
	else:
		price = split[4]
		priceValue = price[1:5]	

	priceValue = float(priceValue)
	trip = {'Date': date,'Departure Time': departTime, 'Arrival Time': arriveTime, 'Price': priceValue}
	return trip

def initiate():
	print "Opening Megabus Website"
	driver = webdriver.Firefox()
	driver.get("http://ca.megabus.com")
	driver.find_element_by_id('btnEnglishCanada').click()
	return driver

def checkTrips(driver, searchString, dates):
	driver.get(searchString)
	id1 = 'JourneyResylts_OutboundList_GridViewResults_ctl'
	id2 = '_row_item'
	i = 0
	outboundList = []
	inboundList = []
	while True:
		if (i < 10):
			fullID = (id1 + '0' + str(i) + id2)
		else:
			fullID = (id1 + str(i) + id2)
		try:
			trip = driver.find_element_by_id(fullID).text
		except:
			break
		trip = isolateItems(trip, str(dates[0]))
		i = i + 1
		outboundList.append(trip)
	id1 = 'JourneyResylts_InboundList_GridViewResults_ctl'	
	i = 0
	while True:
		if (i < 10):
			fullID = (id1 + '0' + str(i) + id2)
		else:
			fullID = (id1 + str(i) + id2)
		try:
			trip = driver.find_element_by_id(fullID).text
		except:
			break
		trip = isolateItems(trip, str(dates[1]))
		i = i + 1
		inboundList.append(trip)
	return (outboundList, inboundList)

def filterTrips(trips, conditions):
	valid = [[],[]]
	outboundTrips = trips[0]
	inboundTrips = trips[1]
	splitConditions = []
	for item in conditions:
		item = item.split(':')
		splitConditions.append(item)
	depart1 = splitConditions[0]
	depart2 = splitConditions[1]
	arrival1 = splitConditions[2]
	arrival2 = splitConditions[3]
	for trip in outboundTrips:
		departTime = trip['Departure Time']
		departTime = departTime.split(':')
		if int(departTime[0]) > int(depart1[0]) and int(departTime[0]) < int(depart2[0]):
			valid[0].append(trip)
		elif int(departTime[0]) == int(depart1[0]) and int(departTime[1]) > int(depart1[1]):
			valid[0].append(trip)
		elif int(departTime[0]) == int(depart2[0]) and int(departTime[1]) < int(depart1[1]):
			valid[0].append(trip)
	for trip in inboundTrips:
		arrivalTime = trip['Arrival Time']
		arrivalTime = arrivalTime.split(':')
		if int(arrivalTime[0]) > int(arrival1[0]) and int(arrivalTime[0]) < int(arrival2[0]):
			valid[1].append(trip)
		elif int(arrivalTime[0]) == int(arrival1[0]) and int(arrivalTime[1]) > int(arrival1[1]):
			valid[1].append(trip)
		elif int(arrivalTime[0]) == int(arrival2[0]) and int(arrivalTime[1]) < int(arrival1[1]):
			valid[1].append(trip)
	return valid

def printTrips(tripList):
	print "Outbound"
	for item in tripList[0]:
		line = "Date: " + item["Date"] + "\tDeparture Time: " + item["Departure Time"] + "\tArrival Time: " + item["Arrival Time"] + "\tPrice: " + str(item["Price"])
		print line
	print "Inbound"
	for item in tripList[1]:
		line = "Date: " + item["Date"] + "\tDeparture Time: " + item["Departure Time"] + "\tArrival Time: " + item["Arrival Time"] + "\tPrice: " + str(item["Price"])
		print line

def getNextWeekend(d):
	weekend = []	
	d += datetime.timedelta(1)
	while d.weekday() != 4:
		d += datetime.timedelta(1)
	friday = d
	weekend.append(friday.strftime('%d-%m-%Y'))
	d += datetime.timedelta(2)
	sunday = d
	weekend.append(sunday.strftime('%d-%m-%Y'))
	weekend.append(d)
	return weekend

def getBestTrip(bestPrice,tripList):
	outboundTrips = tripList[0]
	inboundTrips = tripList[1]
	currPrice = outboundTrips[0]["Price"]
	currTrip = outboundTrips[0]
	for item in outboundTrips:
		if item["Price"] < currPrice:
			currTrip = item
	bestPrice[0].append(currTrip)
	currPrice = inboundTrips[0]["Price"]
	currTrip = inboundTrips[0]
	for item in inboundTrips:
		if item["Price"] < currPrice:
			currTrip = item
	bestPrice[1].append(currTrip)
	return bestPrice

driver = initiate()
time.sleep(5)
bestPrice = [[],[]]
searchRange = 20
date = datetime.date.today()
for i in range(0,searchRange):
	weekend = getNextWeekend(date)
	print "Searching trips for the weekend of %s" %str(weekend[0])
	searchString = createSearchString(str(weekend[0]), str(weekend[1]))
	trips = checkTrips(driver, searchString, weekend)
	valid = filterTrips(trips, ['17:00', '22:30', '19:30', '23:00'])
	try:
		bestPrice = getBestTrip(bestPrice, valid)
	except:
		break
	date = weekend[2]
printTrips(valid)
printTrips(bestPrice)
driver.close()
