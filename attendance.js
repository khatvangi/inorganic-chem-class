/**
 * CHEM 361 Attendance System
 * QR code check-in with instructor dashboard
 */

// state
const state = {
    user: null, // { id, name, role: 'student' | 'instructor' }
    schedule: null,
    currentCode: null,
    codeExpiry: null,
    attendance: {}, // { date: { studentId: { name, time } } }
};

// storage keys
const STORAGE_KEYS = {
    user: 'chem361-user',
    attendance: 'chem361-attendance',
    currentCode: 'chem361-code',
};

// UI elements
const ui = {
    loginView: document.getElementById('loginView'),
    studentView: document.getElementById('studentView'),
    instructorView: document.getElementById('instructorView'),
    loginForm: document.getElementById('loginForm'),
    studentId: document.getElementById('studentId'),
    studentName: document.getElementById('studentName'),
    instructorBtn: document.getElementById('instructorBtn'),
    welcomeName: document.getElementById('welcomeName'),
    logoutBtn: document.getElementById('logoutBtn'),
    instrLogoutBtn: document.getElementById('instrLogoutBtn'),
    // student
    todayDate: document.getElementById('todayDate'),
    todayTopic: document.getElementById('todayTopic'),
    todayBadge: document.getElementById('todayBadge'),
    checkinArea: document.getElementById('checkinArea'),
    checkedInArea: document.getElementById('checkedInArea'),
    noClassArea: document.getElementById('noClassArea'),
    checkinCode: document.getElementById('checkinCode'),
    checkinBtn: document.getElementById('checkinBtn'),
    checkinTime: document.getElementById('checkinTime'),
    scheduleList: document.getElementById('scheduleList'),
    statPresent: document.getElementById('statPresent'),
    statAbsent: document.getElementById('statAbsent'),
    statRate: document.getElementById('statRate'),
    // instructor
    instrTodayDate: document.getElementById('instrTodayDate'),
    instrTodayTopic: document.getElementById('instrTodayTopic'),
    qrcode: document.getElementById('qrcode'),
    todayCodeEl: document.getElementById('todayCode'),
    codeTimer: document.getElementById('codeTimer'),
    regenerateBtn: document.getElementById('regenerateBtn'),
    showQRBtn: document.getElementById('showQRBtn'),
    showCodeBtn: document.getElementById('showCodeBtn'),
    classSelect: document.getElementById('classSelect'),
    attendanceBody: document.getElementById('attendanceBody'),
    exportBtn: document.getElementById('exportBtn'),
};

// helpers
const formatDate = (dateStr) => {
    const d = new Date(dateStr + 'T00:00:00');
    return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
};

const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
};

const getTodayStr = () => {
    const d = new Date();
    return d.toISOString().split('T')[0];
};

const generateCode = () => {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    let code = '';
    for (let i = 0; i < 6; i++) {
        code += chars[Math.floor(Math.random() * chars.length)];
    }
    return code;
};

// load schedule
const loadSchedule = async () => {
    try {
        const res = await fetch('./data/schedule.json');
        state.schedule = await res.json();
    } catch (e) {
        console.error('Failed to load schedule:', e);
    }
};

// load attendance from storage
const loadAttendance = () => {
    const stored = localStorage.getItem(STORAGE_KEYS.attendance);
    if (stored) {
        state.attendance = JSON.parse(stored);
    }
};

// save attendance
const saveAttendance = () => {
    localStorage.setItem(STORAGE_KEYS.attendance, JSON.stringify(state.attendance));
};

// load user
const loadUser = () => {
    const stored = localStorage.getItem(STORAGE_KEYS.user);
    if (stored) {
        state.user = JSON.parse(stored);
    }
};

// save user
const saveUser = () => {
    localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(state.user));
};

// get today's class
const getTodaysClass = () => {
    if (!state.schedule) return null;
    const today = getTodayStr();
    return state.schedule.classes.find(c => c.date === today);
};

// get class by date
const getClassByDate = (dateStr) => {
    if (!state.schedule) return null;
    return state.schedule.classes.find(c => c.date === dateStr);
};

// show view
const showView = (viewName) => {
    ui.loginView.classList.remove('active');
    ui.studentView.classList.remove('active');
    ui.instructorView.classList.remove('active');

    if (viewName === 'login') ui.loginView.classList.add('active');
    else if (viewName === 'student') ui.studentView.classList.add('active');
    else if (viewName === 'instructor') ui.instructorView.classList.add('active');
};

// render student dashboard
const renderStudentDashboard = () => {
    if (!state.user) return;

    ui.welcomeName.textContent = state.user.name.split(' ')[0];

    const todayClass = getTodaysClass();
    const today = getTodayStr();

    if (todayClass) {
        ui.todayDate.textContent = formatDate(todayClass.date);
        ui.todayTopic.textContent = todayClass.topic;

        // unit badge
        ui.todayBadge.className = `unit-badge unit-${todayClass.unit}`;
        ui.todayBadge.textContent = `Unit ${todayClass.unit}`;

        if (todayClass.noClass) {
            ui.checkinArea.classList.add('hidden');
            ui.checkedInArea.classList.add('hidden');
            ui.noClassArea.classList.remove('hidden');
        } else {
            ui.noClassArea.classList.add('hidden');
            // check if already checked in
            const todayAttendance = state.attendance[today];
            if (todayAttendance && todayAttendance[state.user.id]) {
                ui.checkinArea.classList.add('hidden');
                ui.checkedInArea.classList.remove('hidden');
                ui.checkinTime.textContent = `at ${todayAttendance[state.user.id].time}`;
            } else {
                ui.checkinArea.classList.remove('hidden');
                ui.checkedInArea.classList.add('hidden');
            }
        }
    } else {
        ui.todayDate.textContent = formatDate(today);
        ui.todayTopic.textContent = 'No class scheduled';
        ui.todayBadge.classList.add('hidden');
        ui.checkinArea.classList.add('hidden');
        ui.checkedInArea.classList.add('hidden');
        ui.noClassArea.classList.remove('hidden');
    }

    // render schedule
    renderSchedule();

    // render stats
    renderStats();
};

// render schedule list
const renderSchedule = () => {
    if (!state.schedule) return;

    const today = getTodayStr();
    let html = '';

    state.schedule.classes.forEach(cls => {
        const isPast = cls.date < today;
        const isToday = cls.date === today;
        const isNoClass = cls.noClass;

        let statusClass = '';
        if (isToday) statusClass = 'today';
        else if (isPast) statusClass = 'past';
        if (isNoClass) statusClass += ' no-class';

        // attendance status
        let attendanceMark = '';
        if (!isNoClass && !cls.exam) {
            const dayAttendance = state.attendance[cls.date];
            if (dayAttendance && dayAttendance[state.user?.id]) {
                attendanceMark = '<div class="attendance-mark present">✓</div>';
            } else if (isPast) {
                attendanceMark = '<div class="attendance-mark absent">✗</div>';
            } else {
                attendanceMark = '<div class="attendance-mark pending"></div>';
            }
        }

        html += `
            <div class="schedule-item ${statusClass}">
                <div class="schedule-date">${formatDate(cls.date)}</div>
                <div class="schedule-topic">${cls.topic}</div>
                ${attendanceMark}
            </div>
        `;
    });

    ui.scheduleList.innerHTML = html;
};

// render stats
const renderStats = () => {
    if (!state.schedule || !state.user) return;

    const today = getTodayStr();
    let present = 0;
    let total = 0;

    state.schedule.classes.forEach(cls => {
        if (cls.noClass || cls.exam) return;
        if (cls.date > today) return; // future class

        total++;
        const dayAttendance = state.attendance[cls.date];
        if (dayAttendance && dayAttendance[state.user.id]) {
            present++;
        }
    });

    const absent = total - present;
    const rate = total > 0 ? Math.round((present / total) * 100) : 0;

    ui.statPresent.textContent = present;
    ui.statAbsent.textContent = absent;
    ui.statRate.textContent = `${rate}%`;
};

// student check-in
const handleCheckin = () => {
    const enteredCode = ui.checkinCode.value.trim().toUpperCase();
    const today = getTodayStr();

    // load current code from storage (set by instructor)
    const storedCode = localStorage.getItem(STORAGE_KEYS.currentCode);
    let codeData = null;
    if (storedCode) {
        codeData = JSON.parse(storedCode);
    }

    // validate code
    if (!codeData || codeData.date !== today) {
        alert('No active attendance code for today. Please ask your instructor.');
        return;
    }

    if (codeData.code !== enteredCode) {
        alert('Invalid code. Please try again.');
        return;
    }

    // check expiry
    if (new Date() > new Date(codeData.expiry)) {
        alert('This code has expired. Please ask your instructor for a new code.');
        return;
    }

    // record attendance
    if (!state.attendance[today]) {
        state.attendance[today] = {};
    }

    state.attendance[today][state.user.id] = {
        name: state.user.name,
        time: formatTime(new Date()),
    };

    saveAttendance();
    renderStudentDashboard();
};

// instructor functions
const renderInstructorDashboard = () => {
    const todayClass = getTodaysClass();
    const today = getTodayStr();

    if (todayClass) {
        ui.instrTodayDate.textContent = formatDate(todayClass.date);
        ui.instrTodayTopic.textContent = todayClass.topic;
    } else {
        ui.instrTodayDate.textContent = formatDate(today);
        ui.instrTodayTopic.textContent = 'No class scheduled';
    }

    // load or generate code
    const storedCode = localStorage.getItem(STORAGE_KEYS.currentCode);
    if (storedCode) {
        const codeData = JSON.parse(storedCode);
        if (codeData.date === today && new Date() < new Date(codeData.expiry)) {
            state.currentCode = codeData.code;
            state.codeExpiry = new Date(codeData.expiry);
        } else {
            generateNewCode();
        }
    } else {
        generateNewCode();
    }

    displayCode();
    startCodeTimer();

    // populate class select
    renderClassSelect();

    // render attendance table
    renderAttendanceTable(today);
};

const generateNewCode = () => {
    const today = getTodayStr();
    state.currentCode = generateCode();
    state.codeExpiry = new Date(Date.now() + 15 * 60 * 1000); // 15 minutes

    const codeData = {
        code: state.currentCode,
        date: today,
        expiry: state.codeExpiry.toISOString(),
    };

    localStorage.setItem(STORAGE_KEYS.currentCode, JSON.stringify(codeData));
};

const displayCode = () => {
    ui.todayCodeEl.textContent = state.currentCode;

    // generate QR code
    ui.qrcode.innerHTML = '';
    if (typeof QRCode !== 'undefined') {
        QRCode.toCanvas(document.createElement('canvas'), state.currentCode, {
            width: 200,
            margin: 2,
            color: { dark: '#000', light: '#fff' },
        }, (err, canvas) => {
            if (!err) {
                ui.qrcode.appendChild(canvas);
            }
        });
    }
};

let timerInterval = null;
const startCodeTimer = () => {
    if (timerInterval) clearInterval(timerInterval);

    const updateTimer = () => {
        if (!state.codeExpiry) return;

        const remaining = Math.max(0, state.codeExpiry - new Date());
        const mins = Math.floor(remaining / 60000);
        const secs = Math.floor((remaining % 60000) / 1000);

        ui.codeTimer.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;

        if (remaining <= 0) {
            clearInterval(timerInterval);
            ui.codeTimer.textContent = 'EXPIRED';
        }
    };

    updateTimer();
    timerInterval = setInterval(updateTimer, 1000);
};

const renderClassSelect = () => {
    if (!state.schedule) return;

    let html = '';
    state.schedule.classes.forEach(cls => {
        if (cls.noClass) return;
        html += `<option value="${cls.date}">${formatDate(cls.date)} - ${cls.topic.substring(0, 30)}</option>`;
    });

    ui.classSelect.innerHTML = html;

    // set to today if available
    const today = getTodayStr();
    const todayOption = Array.from(ui.classSelect.options).find(o => o.value === today);
    if (todayOption) {
        ui.classSelect.value = today;
    }
};

const renderAttendanceTable = (dateStr) => {
    const dayAttendance = state.attendance[dateStr] || {};
    let html = '';

    const entries = Object.entries(dayAttendance);
    if (entries.length === 0) {
        html = '<tr><td colspan="4" style="text-align: center; color: var(--text-muted);">No attendance records</td></tr>';
    } else {
        entries.forEach(([studentId, data]) => {
            html += `
                <tr>
                    <td style="font-family: 'JetBrains Mono', monospace;">${studentId}</td>
                    <td>${data.name}</td>
                    <td>${data.time}</td>
                    <td><span class="attendance-mark present" style="display: inline-flex;">✓</span></td>
                </tr>
            `;
        });
    }

    ui.attendanceBody.innerHTML = html;
};

const exportAttendance = () => {
    if (!state.schedule) return;

    // build CSV
    let csv = 'Student ID,Name';

    // add dates as columns
    state.schedule.classes.forEach(cls => {
        if (!cls.noClass && !cls.exam) {
            csv += `,${cls.date}`;
        }
    });
    csv += '\n';

    // gather all students
    const allStudents = {};
    Object.values(state.attendance).forEach(dayData => {
        Object.entries(dayData).forEach(([id, data]) => {
            if (!allStudents[id]) {
                allStudents[id] = data.name;
            }
        });
    });

    // add rows
    Object.entries(allStudents).forEach(([id, name]) => {
        csv += `${id},${name}`;
        state.schedule.classes.forEach(cls => {
            if (!cls.noClass && !cls.exam) {
                const dayData = state.attendance[cls.date];
                csv += `,${dayData && dayData[id] ? 'P' : 'A'}`;
            }
        });
        csv += '\n';
    });

    // download
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chem361-attendance-${getTodayStr()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
};

// event listeners
const setupListeners = () => {
    // login form
    ui.loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const id = ui.studentId.value.trim().toUpperCase();
        const name = ui.studentName.value.trim();

        if (!id || !name) {
            alert('Please enter both Student ID and Name');
            return;
        }

        state.user = { id, name, role: 'student' };
        saveUser();
        showView('student');
        renderStudentDashboard();
    });

    // instructor login
    ui.instructorBtn.addEventListener('click', () => {
        const password = prompt('Enter instructor password:');
        if (password === 'chem361') { // simple password for demo
            state.user = { id: 'INSTRUCTOR', name: 'Instructor', role: 'instructor' };
            saveUser();
            showView('instructor');
            renderInstructorDashboard();
        } else {
            alert('Invalid password');
        }
    });

    // logout
    ui.logoutBtn.addEventListener('click', () => {
        state.user = null;
        localStorage.removeItem(STORAGE_KEYS.user);
        showView('login');
    });

    ui.instrLogoutBtn.addEventListener('click', () => {
        state.user = null;
        localStorage.removeItem(STORAGE_KEYS.user);
        showView('login');
    });

    // check-in
    ui.checkinBtn.addEventListener('click', handleCheckin);
    ui.checkinCode.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleCheckin();
    });

    // regenerate code
    ui.regenerateBtn.addEventListener('click', () => {
        generateNewCode();
        displayCode();
        startCodeTimer();
    });

    // class select change
    ui.classSelect.addEventListener('change', () => {
        renderAttendanceTable(ui.classSelect.value);
    });

    // export
    ui.exportBtn.addEventListener('click', exportAttendance);

    // QR/Code toggle
    ui.showQRBtn.addEventListener('click', () => {
        ui.showQRBtn.classList.add('active');
        ui.showCodeBtn.classList.remove('active');
        ui.qrcode.classList.remove('hidden');
    });

    ui.showCodeBtn.addEventListener('click', () => {
        ui.showCodeBtn.classList.add('active');
        ui.showQRBtn.classList.remove('active');
        ui.qrcode.classList.add('hidden');
    });
};

// init
const init = async () => {
    await loadSchedule();
    loadAttendance();
    loadUser();
    setupListeners();

    // route to correct view
    if (state.user) {
        if (state.user.role === 'instructor') {
            showView('instructor');
            renderInstructorDashboard();
        } else {
            showView('student');
            renderStudentDashboard();
        }
    } else {
        showView('login');
    }
};

init();
