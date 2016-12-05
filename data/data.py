import sys
import csv
import random
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError


def setfilename(yr, month):
    filename_plus = "-citibike-tripdata"
    if (month >= 10):
        filename = str(yr) + str(month) + filename_plus
    else:
        filename = str(yr) + '0' + str(month) + filename_plus
    return filename


def getdata(filename):
    try:
        with open(filename + ".csv") as csvfile:
            data = csv.reader(csvfile, dialect='excel')
            datalist = list(data)
    except IOError:
        print "Error: Could not find " + filename + ".csv"
        sys.exit(1)
    return datalist


def writedata(data_result, filename):
    try:
        with open("./sample/" + filename + ".csv", 'w') as csvfile:
            wr = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_NONNUMERIC)
            wr.writerow(["date", "tripduration", "start", "birthdate", "gender", "precipitation", "snowdepth", "avgtemp", "avgwind"])
            wr.writerows(data_result)
    except IOError:
        print "Error: Could not write " + filename + ".csv"
        sys.exit(1)


def mergedata(trip, weather):
    for i in trip:
        for j in weather:
            if i[0] == j[2]:
                i.append(j[3])
                i.append(j[4])
                i.append(float(j[6]) + float(j[7]) / 2)
                i.append(j[8])
    return trip


def removeHead(data1, data2, data3):
    del data1[0]
    del data2[0]
    del data3[0]
    return data1, data2, data3


def addheader(data):
    row = ["date", "tripduration", "start", "birthdate", "gender", "precipitation", "snowdepth", "avgtemp", "avgwind"]
    data[:0] = row
    return data


def removeNull(data):
    modified = []
    for i in range(len(data)):
        if data[i][14] == '0':
            continue
        else:
            modified.append(data[i])
    return modified


def addDate(data):
    for row in data:
        dt = convertDateTime(row[1])[:-9]
        row[:0] = [dt]
    return data


def convertDateTime(element):
    if eval_YMD(element) is True:
        return element
    else:
        if eval_MDY(element) is True:
            element = datetime.strptime(element, '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            return element
        elif eval_HM(element) is True:
            element = datetime.strptime(element, '%m/%d/%Y %H:%M').strftime('%Y-%m-%d %H:%M:%S')
            return element
        else:
            print "Date format " + element + " is not considered."


def eval_YMD(d):
    try:
        datetime.strptime(d, '%Y-%m-%d %H:%M:%S')
        return True
    except ValueError:
        return False


def eval_MDY(d):
    try:
        datetime.strptime(d, '%m/%d/%Y %H:%M:%S')
        return True
    except ValueError:
        return False


def eval_HM(d):
    try:
        datetime.strptime(d, '%m/%d/%Y %H:%M')
        return True
    except ValueError:
        return False


def convertWeatherTime(data):
    for row in data:
        row[2] = datetime.strptime(row[2], '%m/%d/%y').strftime('%Y-%m-%d')
    return data


def reducedata(data):
    for row in data:
        del row[5:14]
        del row[2:4]
    return data


def sampling(data):
    num = int(len(data) * 0.01) # Monthly data's 0.01%
    sample = [data[i] for i in sorted(random.sample(xrange(len(data)), num))]
    return sample


def convertLocation(data):
    for row in data:
        start = row[2] + ", " + row[3]
        end = row[4] + ", " + row[5]
        zipcode_start = requestLocation(start)
        zipcode_end = requestLocation(end)
        del row[2:6]
        row.append(zipcode_start[-31:-26])
        row.append(zipcode_end[-31:-26])
    return data


def requestLocation(coordinate):
    geolocator = Nominatim()
    try:
        return geolocator.reverse(coordinate, timeout=4000)
    except GeocoderServiceError as e:
        if e.message == 'HTTP Error 420: unused':
            time.sleep(60)
            return geolocator.reverse(coordinate, timeout=4000)
        elif e.message == 'HTTP Error 429: Too Many Requests':
            time.sleep(60)
            return geolocator.reverse(coordinate, timeout=4000)
        elif e.message == '<urlopen error [Errno 10060] A connection attempt failed because the connected party did not properly respond after a period of time, or established connection failed because connected host has failed to respond>':
            time.sleep(60)
            return geolocator.reverse(coordinate, timeout=4000)
        elif e.message == '<urlopen error [Errno 11004] getaddrinfo failed>':
            time.sleep(1800)
            return geolocator.reverse(coordinate, timeout=4000)
        elif e.message == '<urlopen error [Errno 10054] An existing connection was forcibly closed by the remote host>':
            time.sleep(1800)
            return geolocator.reverse(coordinate, timeout=4000)
        elif e.message == '<urlopen error [Errno 10053] An established connection was aborted by the software in your host machine>':
            time.sleep(1800)
            return geolocator.reverse(coordinate, timeout=4000)
        else:
            print e.message


def addstationzip(data, station):
    available = []
    for i in data:
        for j in station:
            if i[4] == j[1]:
                i[3] = j[12]
    for row in data:
        if int(row[3]) > 10000 and int(row[3]) < 10300:
            available.append(row)
    return available


def process(data_raw, data_weather, data_station):
    data_nohead, data_weather, data_station = removeHead(data_raw, data_weather, data_station)
    data_zip = addstationzip(data_raw, data_station)
    data_removed = removeNull(data_zip)
    data_sample = sampling(data_removed)
    data_notime = addDate(data_sample)
    data_reduced = reducedata(data_notime)
    data_weather = convertWeatherTime(data_weather)
    data_merged = mergedata(data_reduced, data_weather)
    # data_result = convertLocation(data_fixed)
    return data_merged


def main():
    counter = 1
    for yr in range(2013, 2017):
        for month in range(1, 13):
            if (yr == 2013 and month < 7) or (yr == 2016 and month > 6):
                continue
            filename = setfilename(yr, month)
            # DATA INPUT1
            data_raw = getdata(filename)
            data_weather = getdata("central_park_weather")
            data_station = getdata("citibike-station")
            print "Data length: " + str(len(data_raw))            
            print str(counter) + ". " + filename + " is read."
            # DATA MANIPULATION
            data_result = process(data_raw, data_weather, data_station)
            # DATA OUTPUT
            writedata(data_result, filename)
            print str(counter) + ". " + filename + " is written."
            print "Data length: " + str(len(data_result))
            counter += 1


if __name__ == "__main__":
    main()
