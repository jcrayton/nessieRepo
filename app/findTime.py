#findTime.py
from __future__ import print_function
from apiclient import discovery
import httplib2
from flask import render_template, Flask, request, json, redirect, url_for, jsonify
import os
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import google.oauth2.credentials
from app import app
import datetime
import calendar
import pandas as pd #pip install pandas
from .format import *
from .timeSlot import *
from .time import *

#Find open time slots for events.
class FindTime:
    def __init__(self, service, dueDate, current):
        """
        Keyword arguments:
        service -- string representing the service code for the logged in user
        dueDate -- string representing the user's inputted assignment dueDate
        current -- string representing the current date and time
        """
        self.service = service
        self.dueDate = dueDate
        self.current = current
        pass


    def findAvailableTimes(self, nowDay, nowHour, nowMinute, workStart, workEnd, events, timeEst):
        """Calculate every available time slot in relation to the events on the user's
        calender from now until the assignment due date. Return a list of these time slots.

        Keyword arguments:
        nowDay -- int of the current day
        nowHour -- int of the current hour
        nowMinute -- int of the current minute
        workStart -- int representing the time when the program starts scheduling events
        workEnd -- int representing the time when the program stops scheduling events
        events -- list of Google Calendar events in dictionary form
        timeEst -- int representing user's inputted event length value
        """
        global format
        format = Format()
        global timeSlot
        timeSlot = TimeSlot(timeEst)
        global availableTimes
        availableTimes = []
        print(self.current)
        try:
            if len(events) > 1:
                for i in range(len(events) - 1):

                    event1 = events[i]
                    event2 = events[i + 1]
                    e1, e2 = format.formatEvent(event1, event2)
                    self.compareEvents(e1, e2, workStart, workEnd, nowDay, nowHour, nowMinute, timeEst)

                lastEvent = events[len(events) - 1]
                secondToLast = events[len(events) - 2]
                self.compareLastEvent(lastEvent, secondToLast, workStart, workEnd, nowDay, nowHour, nowMinute, timeEst)

            elif len(events) == 1:
                lastEvent = events[0]
                nowTime = [self.current[:11] + str(int(self.current[11:13]) - 1) + self.current[13:], self.current]
                nowTime = format.eventFormatDictionary(nowTime, 'now')

                self.compareLastEvent(lastEvent, nowTime, workStart, workEnd, nowDay, nowHour, nowMinute, timeEst)

            self.addEmptyDays(events, workStart, workEnd, timeEst)
            availableTimes.sort()
            return availableTimes
        except:
            global msg
            msg = "There isn't enough time. Try again"
            return redirect('/error')


    def openTimeWindow(self, workStart, workEnd):
        """Return the time during the day when the user can work on assignments
        in terms of hours and in terms of the minutes out of the entire minutes
        in a day.

        Keyword arguments:
        workStart -- int representing the time when the program starts scheduling events
        workEnd -- int representing the time when the program stops scheduling events
        """
        openTime = range(workStart, workEnd)
        return openTime


    def compareEvents(self, e1, e2, workStart, workEnd, nowDay, nowHour, nowMinute, timeEst):
        """Compare each pair of events on the user's calendar from now until the
        entered deadline. If there is enough time between the events, add the time slot
        between them to the list of available times.

        Keyword arguments:
        e1 -- the first event in the pair being compared
        e2 -- the second event in the part being compared
        workStart -- int representing the time when the program starts scheduling events
        workEnd -- int representing the time when the program stops scheduling events
        nowDay -- int of the current day
        nowHour -- int of the current hour
        nowMinute -- int of the current minute
        timeEst -- int representing user's inputted event length value
        """
        estTimeMin = timeEst * 60
        estMins = estTimeMin % 60
        estHours = (estTimeMin - estMins) / 60
        openTime = self.openTimeWindow(workStart, workEnd)

        sameDay = (e1.day == e2.day)

        #for time in morning before eventTime
        morningTime = (e2.hour * 60 + e2.minute) - (workStart)
        enoughMorningTime = morningTime >= estTimeMin + 30

        # For events on the same day
        timeDiff = (e2.hour * 60 + e2.minute) - (e1.hour * 60 + e1.minute)
        enoughTime = timeDiff >= (estTimeMin + 30)

        # For events on different days
        timeDiff2 = (1440 - (e1.hour * 60) + e1.minute) + (e2.hour * 60 + e2.minute)
        enoughTime2 = timeDiff2 >= (estTimeMin + 30)

        # Ensures that the algorithm doesn't schedule events in the past
        now = ((e1.hour == nowHour) and (e1.minute >= nowMinute)) or e1.hour > nowHour or (e1.day > nowDay)

        # Ensures that the entire scheduled event would be within the open working hours
        timeWindow = (e1.hour * 60) + e1.minute + (estTimeMin + 30)

        if(now and (sameDay and enoughTime and ((e1.hour*60) in openTime) and (timeWindow in openTime))):
            time = timeSlot.afterTimeSlot(e1)
            availableTimes.append(time)

        if(now and (not sameDay and enoughTime2 and ((e1.hour*60) in openTime) and (timeWindow in openTime))):
            time = timeSlot.afterTimeSlot(e1)
            availableTimes.append(time)

        if(not sameDay and enoughMorningTime):
            time = timeSlot.beforeTimeSlot(e2)
            availableTimes.append(time)


    def compareLastEvent(self, lastEvent, secondToLast, workStart, workEnd, nowDay, nowHour, nowMinute, timeEst):
        """Account for finding the time slots around the the last event before the
        deadline. Also account for if there is only one event before the deadline.

        Keyword arguments:
        lastEvent -- final event before the due date in dictionary form
        secondToLast -- second to last event before the due date in dictionary form
        workStart -- int representing the time when the program starts scheduling events
        workEnd -- int representing the time when the program stops scheduling events
        nowDay -- int of the current day
        nowHour -- int of the current hour
        nowMinute -- int of the current minute
        timeEst -- int representing user's inputted event length value
        """
        estTimeMin = timeEst * 60
        estMins = estTimeMin % 60
        estHours = (estTimeMin - estMins) / 60
        openTime = self.openTimeWindow(workStart, workEnd)

        lastEnd, lastStart = format.formatEvent(lastEvent, lastEvent)
        secondEnd, secondStart = format.formatEvent(secondToLast, secondToLast)

        timeWindow = (lastEnd.hour * 60) + lastEnd.minute + (estTimeMin + 30)

        beforeTime = (lastStart.hour * 60 + lastStart.minute) - (workStart)
        enoughBeforeTime = (beforeTime >= estTimeMin + 30)

        timeDiff = (lastStart.hour * 60 + lastStart.minute) - (nowHour * 60 + nowMinute)
        enoughTime = (timeDiff >= (estTimeMin + 30))

        timeDiffEvent = (lastStart.hour * 60 + lastStart.minute) - (secondEnd.hour * 60 + secondEnd.minute)
        enoughTimeEvent = (timeDiffEvent >= (estTimeMin + 30))

        diffDays = lastStart.day != nowDay
        diffEventDays = lastStart.day != secondEnd.day

        if(enoughBeforeTime and (enoughTime or diffDays) and (diffEventDays or enoughTimeEvent)):
            time = timeSlot.beforeTimeSlot(lastStart)
            availableTimes.append(time)

        if(((lastEnd.hour*60) in openTime) and (timeWindow in openTime)):
            time = timeSlot.afterTimeSlot(lastEnd)
            availableTimes.append(time)


    def addEmptyDays(self, events, workStart, workEnd, timeEst):
        """Add morning time slots to availableTimes for each day without events.

        Keyword arguments:
        events -- a list of all events on the user's calendar from now until the due date in dictionary form
        workStart -- int representing the time when the program starts scheduling events
        workEnd -- int representing the time when the program stops scheduling events
        timeEst -- int representing user's inputted event length value
        """
        startMinutes = workStart % 60
        startHours = (workStart - startMinutes) / 60
        endMinutes = workEnd % 60
        endHours = (workEnd - endMinutes) / 60

        enoughTimeEmpty = (workEnd - workStart) >= (timeEst * 60) + 30

        emptyDays = self.getEmptyDays(events)
        for day in emptyDays:
            if enoughTimeEmpty:
                morning = datetime.datetime(int(day[0:4]), int(day[5:7]), int(day[8:]), int(startHours), int(startMinutes))
                morning -= datetime.timedelta(minutes = 15)
                time = timeSlot.afterTimeSlot(morning)
                availableTimes.append(time)


    def getEmptyDays(self, events):
        """Return the list of all days without Google Calendar events from now until the deadline.

        Keyword arguments:
        events -- a list of all events on the user's calendar from now until the due date in dictionary form
        """
        days1 = self.getAllDays()
        cleanedEvents = []

        for event in events:
            dt = event['start'].get('dateTime')
            cleanedEvents.append(dt)

        days = self.getComparableDateValues(days1)
        events = self.getComparableDateValues(cleanedEvents)

        #Source for removing duplicates:
        #https://stackoverflow.com/questions/18194968/python-remove-duplicates-from-2-lists
        days = [time for time in days if not time in events]
        return days


    def getAllDays(self):
        """Return a list of all the days between now and the user's deadline."""
        start = str(self.current[0:10])
        end = str(self.dueDate[0:10])
        daysRange = pd.date_range(start = start, end = end).tolist()
        daysRange = daysRange[1:len(daysRange)-1]
        days = []
        for i in daysRange:
            day = str(i)
            day = day[:10] + 'T' + day[11:] + '-05:00'
            days.append(day)
        return days


    def getComparableDateValues(self, days):
        """Return a list of days in the required format for comparison.

        Keyword arguments:
        days -- a list of strings representing days
        """
        dates = []
        for i in days:
            date = i[:10]
            dates.append(date)
        return dates
