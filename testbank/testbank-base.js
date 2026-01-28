// shared test bank interaction logic
let totalAnswered = 0;
let totalCorrect = 0;

// get the topic slug from the page for localStorage tracking
const topicSlug = document.body.dataset.topic || 'unknown';

document.addEventListener('DOMContentLoaded', function() {
    // restore any saved progress
    restoreProgress();

    // attach click handlers to all option items
    document.querySelectorAll('.q-options li').forEach(li => {
        li.addEventListener('click', function() {
            const block = this.closest('.q-block');
            if (block.classList.contains('answered')) return;

            // mark block as answered
            block.classList.add('answered');
            totalAnswered++;

            const correctVal = block.dataset.answer;
            const selectedVal = this.dataset.val;
            const isCorrect = selectedVal === correctVal;

            if (isCorrect) {
                this.classList.add('correct');
                totalCorrect++;
            } else {
                this.classList.add('wrong');
                // highlight the correct one
                block.querySelectorAll('.q-options li').forEach(opt => {
                    if (opt.dataset.val === correctVal) opt.classList.add('correct');
                });
            }

            // disable all options
            block.querySelectorAll('.q-options li').forEach(opt => opt.classList.add('disabled'));

            // auto-reveal answer
            const answerDiv = block.querySelector('.q-answer');
            answerDiv.classList.add('visible');

            // hide the reveal button
            const revealBtn = block.querySelector('.q-reveal-btn');
            if (revealBtn) revealBtn.style.display = 'none';

            updateScore();
            saveProgress();
        });
    });
});

function revealAnswer(btn) {
    const block = btn.closest('.q-block');
    const answerDiv = block.querySelector('.q-answer');
    answerDiv.classList.add('visible');
    btn.style.display = 'none';
}

function updateScore() {
    const pill = document.getElementById('scorePill');
    if (pill) pill.textContent = totalCorrect + ' / ' + totalAnswered;

    // show summary if all answered
    const totalQ = document.querySelectorAll('.q-block').length;
    if (totalAnswered >= totalQ) {
        const summary = document.getElementById('scoreSummary');
        if (summary) {
            summary.style.display = 'block';
            const finalEl = document.getElementById('finalScore');
            if (finalEl) finalEl.textContent = totalCorrect + ' / ' + totalQ;
        }
    }
}

function resetAll() {
    totalAnswered = 0;
    totalCorrect = 0;
    document.querySelectorAll('.q-block').forEach(block => {
        block.classList.remove('answered');
        block.querySelectorAll('.q-options li').forEach(li => {
            li.classList.remove('correct', 'wrong', 'selected', 'disabled');
        });
        block.querySelector('.q-answer').classList.remove('visible');
        const btn = block.querySelector('.q-reveal-btn');
        if (btn) btn.style.display = '';
    });
    const pill = document.getElementById('scorePill');
    if (pill) pill.textContent = '0 / 0';
    const summary = document.getElementById('scoreSummary');
    if (summary) summary.style.display = 'none';
    clearProgress();
    window.scrollTo({top: 0, behavior: 'smooth'});
}

// -- localStorage persistence --
function saveProgress() {
    const totalQ = document.querySelectorAll('.q-block').length;
    const data = { answered: totalAnswered, correct: totalCorrect, total: totalQ };
    try { localStorage.setItem('testbank_' + topicSlug, JSON.stringify(data)); } catch(e) {}
}

function restoreProgress() {
    // restore is intentionally not implemented for now —
    // answering questions is a one-pass experience per visit.
    // localStorage stores the last-completed score for the hub page.
}

function clearProgress() {
    try { localStorage.removeItem('testbank_' + topicSlug); } catch(e) {}
}
