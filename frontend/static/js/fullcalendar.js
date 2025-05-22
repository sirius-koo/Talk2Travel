async function fetchJSON(url, opts = {}) { const r = await fetch(url, opts); return r.json(); }

document.addEventListener('DOMContentLoaded', function () {
  const cal = new FullCalendar.Calendar(document.getElementById('calendar'), {
    locale: 'ko',
    initialView: 'dayGridMonth',
    selectable: true,
    select: info => {
      const start = info.start;
      const end = info.end;
      const dayCount = (end - start) / (1000*60*60*24);
      if (dayCount === 1) {
        // alert(`선택한 날짜: ${info.startStr}`);

        console.log(`선택한 시작일: ${info.startStr}`);
      } else {
        // end는 포함되지 않으므로, 1일 빼기
        const realEnd = new Date(end.getTime() - 1*24*60*60*1000);
        const yyyy = realEnd.getFullYear();
        const mm = String(realEnd.getMonth()+1).padStart(2, '0');
        const dd = String(realEnd.getDate()).padStart(2, '0');
        const realEndStr = `${yyyy}-${mm}-${dd}`;
        // alert(`선택한 기간: ${info.startStr} ~ ${realEndStr}`);

        console.log(`선택한 시작일: ${info.startStr}, 종료일: ${realEndStr}`);
      }
    }
  });
  cal.render();
});



function openTripModal(calendar, info) {
  const m = new bootstrap.Modal('#tripModal');
  const form = document.getElementById('tripForm');
  form.start.value = info.startStr;
  form.end.value   = info.endStr;
  m.show();

  form.onsubmit = async ev => {
    ev.preventDefault();
    const body = Object.fromEntries(new FormData(form));
    const saved = await fetchJSON('/api/schedules', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
    calendar.addEvent(saved);
    m.hide();
  };
}