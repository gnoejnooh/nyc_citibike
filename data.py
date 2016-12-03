import sys
import csv
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
        with open("./result/" + filename + ".csv", 'w') as csvfile:
            wr = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_NONNUMERIC)
            wr.writerows(data_result)
    except IOError:
        print "Error: Could not write " + filename + ".csv"
        sys.exit(1)


def mergedata(data1, data2):
    return data1

def removeNull(data):
    modified = []
    for i in range(len(data)):
        if data[i][14] == '0':
            continue
        else:
            modified.append(data[i])
    return modified

def removeTime(data):
    for row in data:
        if row[0] == "tripduration":
            row[:0] = ["date"]
            continue
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


def reducedata(data):
    for row in data:
        del row[12:14]
        del row[8:10]
        del row[2:6]
    return data


def convertLocation(data):
    for row in data:
        if row[0] == "date":
            row.append("startstation")
            row.append("endstation")
            continue
        start = row[2] + ", " + row[3]
        end = row[4] + ", " + row[5]
        zipcode_start = geolocator.reverse(start)[-31:-26]
        time.sleep()
        zipcode_end = geolocator.reverse(end)[-31:-26]
        time.sleep()
        del row[2:6]
        row.append(zipcode_start)
        row.append(zipcode_end)
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


def main():
    counter = 1
    for yr in range(2013, 2014):
        # for yr in range(2015,2017):
        for month in range(7, 8):
            # for month in range(1,13):
            if (yr == 2013 and month < 7) or (yr == 2016 and month > 9):
                # if (yr == 2014 and month < 9) or (yr == 2016 and month > 9):
                continue
            filename = setfilename(yr, month)
            # DATA INPUT
            data_raw = getdata(filename)
            print "Data length: " + str(len(data_raw))
            # data_weather = getdata("central_park_weather")
            print str(counter) + ". " + filename + " is read."
            # DATA MANIPULATION
            data_removed = removeNull(data_raw)
            data_notime = removeTime(data_removed)
            data_reduced = reducedata(data_notime)
            # data_location = convertLocation(data_reduced)
            data_result = data_reduced
            # DATA OUTPUT
            writedata(data_result, filename)
            print str(counter) + ". " + filename + " is written."
            print "Data length: " + str(len(data_result))
            counter += 1


if __name__ == "__main__":
    main()
