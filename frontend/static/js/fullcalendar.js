// E:\Capstone1\Talk2Travel\frontend\static\js\fullcalendar.js

// fetch 편의 함수
async function fetchJSON(url, opts = {}) {
  const r = await fetch(url, opts);
  if (!r.ok) throw new Error(`HTTP error ${r.status}`);
  return r.json();
}

// 도시명으로 공항 자동완성 리스트 가져오기
async function suggestAirports(keyword) {
  if (keyword.length < 2) return [];
  return await fetchJSON(`/api/airports?city=${encodeURIComponent(keyword)}`);
}

document.addEventListener('DOMContentLoaded', function () {
  const calendarEl = document.getElementById('calendar');
  const calendar = new FullCalendar.Calendar(calendarEl, {
    locale: 'ko',
    initialView: 'dayGridMonth',
    selectable: true,

    // DB에 저장된 일정 불러와 캘린더에 표시
    events: async function(fetchInfo, successCallback, failureCallback) {
      try {
        const schedules = await fetchJSON('/api/schedules');
        const events = schedules.map(s => {
          const endDate = new Date(s.end);
          endDate.setDate(endDate.getDate() + 1); // end는 exclusive
          return {
            id:    s.id,
            title: `${s.departure_airport} → ${s.arrival_airport}`,
            start: s.start,
            end:   endDate.toISOString().split('T')[0]
          };
        });
        successCallback(events);
      } catch (err) {
        console.error(err);
        failureCallback(err);
      }
    },

    // select 시 모달 열기
    select: info => openTripModal(calendar, info)
  });

  calendar.render();

  // 모달 폼 요소
  const form = document.getElementById('tripForm');
  const depInput = document.getElementById('depAirportInput');
  const arrInput = document.getElementById('arrAirportInput');
  const depSug   = document.getElementById('depSuggestions');
  const arrSug   = document.getElementById('arrSuggestions');
  const depCode  = document.getElementById('departureAirport');
  const arrCode  = document.getElementById('arrivalAirport');

  // 자동완성 바인딩 함수
  function bindAuto(inputEl, sugEl, codeEl) {
    inputEl.addEventListener('input', async () => {
      const list = await suggestAirports(inputEl.value.trim());
      sugEl.innerHTML = '';
      sugEl.style.display = list.length ? 'block' : 'none';
      list.forEach(a => {
        const li = document.createElement('li');
        li.className = 'list-group-item list-group-item-action';
        li.textContent = `${a.code} – ${a.name}`;
        li.onclick = () => {
          inputEl.value = a.name;
          codeEl.value  = a.code;
          sugEl.innerHTML = '';
          sugEl.style.display = 'none';
        };
        sugEl.appendChild(li);
      });
    });
  }

  bindAuto(depInput, depSug, depCode);
  bindAuto(arrInput, arrSug, arrCode);

  // 일정 저장 시
  form.addEventListener('submit', async ev => {
    ev.preventDefault();
    const data = Object.fromEntries(new FormData(form));
    const saved = await fetchJSON('/api/schedules', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    calendar.addEvent({
      id:    saved.id,
      title: `${saved.departure_airport} → ${saved.arrival_airport}`,
      start: saved.start,
      end:   (() => {
        const d = new Date(saved.end);
        d.setDate(d.getDate() + 1);
        return d.toISOString().split('T')[0];
      })()
    });

    bootstrap.Modal.getInstance(document.getElementById('tripModal')).hide();
  });
});

function openTripModal(calendar, info) {
  const modal = new bootstrap.Modal(document.getElementById('tripModal'));
  document.querySelector('#tripForm [name=start]').value = info.startStr;

  const realEnd = new Date(info.end.getTime() - 24*60*60*1000);
  const yyyy = realEnd.getFullYear();
  const mm   = String(realEnd.getMonth() + 1).padStart(2, '0');
  const dd   = String(realEnd.getDate()).padStart(2, '0');
  document.querySelector('#tripForm [name=end]').value = `${yyyy}-${mm}-${dd}`;

  modal.show();
}