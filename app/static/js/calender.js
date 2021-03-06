// construct a calendar display on the page.
// Adapt from https://github.com/AnirudhGoel/Productive-Calender

// Initialize variables
var current = new Date();
var currentMonth = current.getMonth();
var currentDate = current.getDate();
var currentYear = current.getFullYear();

//
// Build a calendar layout
//
function calender(month, year) {
    // Creat spaces for days before the day of start and day after the month is ended
    var padding = "";
    var postPadding = "";

    // Determining if Feb has 28 or 29 days
    febDays = ((currentYear % 100 !== 0) && (currentYear % 4 === 0) || (currentYear % 400 === 0)) ? 29 : 28;

    // Setting up arrays for the name of the months, days, and the number of days in the month.
    var monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    var dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    var numberOfDays = ["31", String(febDays), "31", "30", "31", "30", "31", "31", "30", "31", "30", "31"];

    // Using (month + 1) because this function uses Jan as 1, Feb as 2, so on.
    var firstDate = new Date(monthNames[month] + ' 1, ' + year);
    var firstDay = firstDate.getDay();
    var totalDays = numberOfDays[month];

    // After getting the first day of the week for the month, padding the other days for that week with the previous months days, i.e., if the first day of the week is on a Thursday, then this fills in Sun - Wed with the last months dates, counting down from the last day on Wed, until Sunday.
    for (var i = 0; i < firstDay; i++) {
        padding += "<div class='preMonth day col-sm p-2 border border-left-0 border-top-0 text-truncate d-none d-sm-inline-block bg-light text-muted'></div>";
    }

    // Adding days in the month to the calendar display
    var generateDay = firstDay;
    var generateCal = "";

    for (var i = 1; i <= totalDays; i++) {
        // Determining when to start a new row
        if (generateDay > 6) {
            generateCal += "<div class='w-100'></div>";
            generateDay = 0;
        }

        // Checking to see if i is equal to the current day, if so then we are making the color of that cell a different color using CSS.
        if (i == currentDate && month == currentMonth) {
            generateCal += "<div class='currentday day col-sm p-2 border border-left-0 border-top-0 text-truncate'><h5 class='row align-items-center'><span class='date col-1'>" + i + "</span><span class='col-1'></span></h5><div class='text-truncate day-container' id='" + i + monthNames[month] + year+"'></div></div>";
            // console.log(i + monthNames[month] + year)
        } else {
            generateCal += "<div class='day col-sm p-2 border border-left-0 border-top-0 text-truncate '><h5 class='row align-items-center'><span class='date col-1'>" + i + "</span><span class='col-1'></span></h5><div class='text-truncate day-container' id='" + i + monthNames[month] + year+ "'></div></div>";
            // console.log(i + monthNames[month] + year)
        }

        generateDay++;
    }

    //padding the cells before the first day of next month
    var totalDaysMonth = parseInt(firstDay) + parseInt(totalDays)
    var lastDay = totalDaysMonth%7;
    if (lastDay != 0) {
        for (var i = 0; i < 7-lastDay; i++) {
            postPadding += "<div class='preMonth day col-sm p-2 border border-left-0 border-top-0 text-truncate d-none d-sm-inline-block bg-light text-muted'></div>";
        }
    }
    // console.log(lastDay)

    // Output the calender onto the site.  Also, putting in the month name and days of the week.
    var calenderTable = "<div class='container-fluid'>";
    var monthYear = "<h5 class='display-4 mb-4 text-center'><span class='month'> </span> <span class='year'> </span><div class='mx-auto'><h6 id='arrowLeft' class='d-inline'><i class='fa fa-arrow-left' onclick='prevMonth();'></i></h6><h6 id ='arrowRight' class='d-inline'> <i class='fa fa-arrow-right' onclick='nextMonth();'></i></h6></div><h5>"
    if ($(window).width() < 768) {
        calenderTable += "<header>"+monthYear+"<div class='row d-none d-sm-flex p-1 bg-dark text-white'> <h6 class='col-sm p-1 text-center'>Sun</h6> <h6 class='col-sm p-1 text-center'>Mon</h6> <h6 class='col-sm p-1 text-center'>Tues</h6> <h6 class='col-sm p-1 text-center'>Wed</h6> <h6 class='col-sm p-1 text-center'>Thur</h6> <h6 class='col-sm p-1 text-center'>Fri</h6> <h6 class='col-sm p-1 text-center'>Sat</h6> </div></header>";
    } else {
        calenderTable += "<header>"+monthYear+"<div class='row d-none d-sm-flex p-1 bg-dark text-white'> <h6 class='col-sm p-1 text-center'>Sunday</h6> <h6 class='col-sm p-1 text-center'>Monday</h6> <h6 class='col-sm p-1 text-center'>Tuesday</h6> <h6 class='col-sm p-1 text-center'>Wednesday</h6> <h6 class='col-sm p-1 text-center'>Thursday</h6> <h6 class='col-sm p-1 text-center'>Friday</h6> <h6 class='col-sm p-1 text-center'>Saturday</h6> </div></header>";
    }
    calenderTable += "<div class='row border border-right-0 border-bottom-0'>";
    calenderTable += padding;
    calenderTable += generateCal;
    calenderTable += postPadding;
    calenderTable += "</div></div>";

    // console.log(calenderTable)

    $(".calender").html(calenderTable);
    $(".month").text(monthNames[month]);
    $(".month").attr('id', month);
    $(".year").text(year);
    $(".year").attr('id', year);
}

//
// Display next month in Calender
//
function nextMonth() {
    if ($(".month").attr('id') != 11) {
        var nextMon = Number($(".month").attr('id')) + 1;
        var year = Number($(".year").attr('id'));
    } else {
        var nextMon = 0;
        var year = Number($(".year").attr('id')) + 1;
    }
    // console.log(nextmon);
    calender(nextMon, year);
    refreshAllEvents(nextMon+1, year);
}

//
// Display previous month in Calender
//
function prevMonth() {
    if ($(".month").attr('id') != 0) {
        var prevMon = Number($(".month").attr('id')) - 1;
        var year = Number($(".year").attr('id'));
    } else {
        var prevMon = 11;
        var year = Number($(".year").attr('id')) - 1;
    }
    // console.log(prevmon);
    calender(prevMon, year);
    refreshAllEvents(prevMon+1, year);
}

//
// Load calender
//
if (window.addEventListener) {
    calender(currentMonth, currentYear);
    refreshAllEvents(currentMonth+1, currentYear);
} else if (window.attachEvent) {
    calender(currentMonth, currentYear);
    refreshAllEvents(currentMonth+1, currentYear);
}

// console.log("load calendar");
