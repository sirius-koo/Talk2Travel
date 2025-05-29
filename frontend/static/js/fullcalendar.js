// fetch 편의 함수
async function fetchJSON(url, opts = {}) {
  const r = await fetch(url, opts);
  return r.json();
}

document.addEventListener('DOMContentLoaded', function () {
  const calendarEl = document.getElementById('calendar');
  const calendar = new FullCalendar.Calendar(calendarEl, {
    locale: 'ko',
    initialView: 'dayGridMonth',
    selectable: true,

    events: async function(fetchInfo, successCallback, failureCallback) {
      try {
        const schedules = await fetchJSON('/api/schedules');
        const events = schedules.map(s => {
          // FullCalendar는 end가 exclusive이므로, 하루 더해줍니다
          const endDate = new Date(s.end);
          endDate.setDate(endDate.getDate() + 1);
          return {
            id:    s.id,
            title: s.city,                   // 제목에 도시명 사용
            start: s.start,                  // YYYY-MM-DD
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

  // 모달 폼 제출 핸들러 등록
  const form = document.getElementById('tripForm');
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
      title: saved.city,
      start: saved.start,
      end: (() => {
        const d = new Date(saved.end);
        d.setDate(d.getDate() + 1);
        return d.toISOString().split('T')[0];
      })()
    });
    
    bootstrap.Modal.getInstance(document.getElementById('tripModal')).hide();
  });
});

function openTripModal(calendar, info) {
  // 1) 모달 객체 준비
  const modal = new bootstrap.Modal(document.getElementById('tripModal'));
  // 2) 날짜 값 세팅 (end는 exclusive라 하루 빼기)
  document.querySelector('#tripForm [name=start]').value = info.startStr;
  const realEnd = new Date(info.end.getTime() - 24*60*60*1000);
  const yyyy = realEnd.getFullYear();
  const mm   = String(realEnd.getMonth()+1).padStart(2, '0');
  const dd   = String(realEnd.getDate()).padStart(2, '0');
  document.querySelector('#tripForm [name=end]').value = `${yyyy}-${mm}-${dd}`;
  // 3) 모달 표시
  modal.show();
}
