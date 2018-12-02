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
import random
import math
import pytz
from pytz import timezone
import time
from tzlocal import get_localzone
import calendar
from .format import *
from .timeSlot import *
from .now import *

# Finds open time slots for events.
class FindTime:
    def __init__(self):
        pass

    def findAvailableTimes(self, nowDay, nowHour, nowMinute, workStart, workEnd, events, timeEst):
        '''Calculates every available time slot in relation to the events on the user's
        calender from now until the assignment due date. Returns a list of these time slots.'''

        global format
        format = Format()
        global timeSlot
        timeSlot = TimeSlot(timeEst)

        for i in range(len(events) - 1):

            event1 = events[i]
            event2 = events[i + 1]
            e1, e2 = format.formatEvent(event1, event2)
            self.compareEvents(e1, e2, workStart, workEnd, nowDay, nowHour, nowMinute, timeEst)

        lastEvent = events[len(events) - 1]
        secondToLast = events[len(events) - 2]
        self.compareLastEvent(lastEvent, secondToLast, workStart, workEnd, nowDay, nowHour, nowMinute, timeEst)

        # print(availableTimes)
        return availableTimes


    def compareLastEvent(self, lastEvent, secondToLast, workStart, workEnd, nowDay, nowHour, nowMinute, timeEst):
        '''Accounts for finding the time slots around the the last event before the
        deadline. Also accounts for if there is only one event before the deadline.'''

        estTimeMin = timeEst * 60
        estMins = estTimeMin % 60
        estHours = (estTimeMin - estMins) / 60
        openHours, openMinutes = self.openTimeWindow(workStart, workEnd)

        lastEnd, lastStart = format.formatEvent(lastEvent, lastEvent)
        secondEnd, secondStart = format.formatEvent(secondToLast, secondToLast)

        timeWindow = (lastEnd.hour * 60) + lastEnd.minute + (estTimeMin + 30)

        beforeTime = (lastStart.hour * 60 + lastStart.minute) - (workStart*60)
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

        if((lastEnd.hour in openHours) and (timeWindow in openMinutes)):
            time = timeSlot.afterTimeSlot(lastEnd)
            availableTimes.append(time)


    def compareEvents(self, e1, e2, workStart, workEnd, nowDay, nowHour, nowMinute, timeEst):
        '''Compares each pair of events on the user's calendar from now until the
        entered deadline. If there is enough time between the events, the time slot
        between them is added to the list of available times.'''

        global availableTimes
        availableTimes = []

        estTimeMin = timeEst * 60
        estMins = estTimeMin % 60
        estHours = (estTimeMin - estMins) / 60
        openHours, openMinutes = self.openTimeWindow(workStart, workEnd)

        sameDay = (e1.day == e2.day)

        #for time in morning before eventTime
        morningTime = (e2.hour * 60 + e2.minute) - (workStart*60)
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

        if(now and (sameDay and enoughTime and (e1.hour in openHours) and (timeWindow in openMinutes))):
            time = timeSlot.afterTimeSlot(e1)
            availableTimes.append(time)

        if(now and (not sameDay and enoughTime2 and (e1.hour in openHours) and (timeWindow in openMinutes))):
            time = timeSlot.afterTimeSlot(e1)
            availableTimes.append(time)

        if(not sameDay and enoughMorningTime):
            time = timeSlot.beforeTimeSlot(e2)
            availableTimes.append(time)

    def openTimeWindow(self, openStartTime, openEndTime):
        '''Returns the time during the day when the user can work on assignments
        in terms of hours and in terms of the minutes out of the entire minutes
        in a day.'''

        openHours = range(openStartTime, openEndTime)
        openMinutes = range(openStartTime * 60, openEndTime * 60)
        return openHours, openMinutes