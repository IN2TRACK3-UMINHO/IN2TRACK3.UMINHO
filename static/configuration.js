const inspectionsFile = document.getElementById('inspections-file');
const maintenanceFile = document.getElementById('maintenance-file');

inspectionsFile.addEventListener('change', (event) => {
    const formData = new FormData();
    formData.append('inspectionsFile', event.target.files[0]);
    fetch(window.location.pathname, {
		method: 'POST',
		body: formData
	})
});

maintenanceFile.addEventListener('change', (event) => {
    const formData = new FormData();
    formData.append('maintenanceFile', event.target.files[0]);
    fetch(window.location.pathname, {
		method: 'POST',
		body: formData
	})
});