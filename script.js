document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('select');
    var instances = M.FormSelect.init(elems);

    // Agrega un evento de cambio al dropdown
    var dropdown = document.getElementById('dropdown-opcion');
    dropdown.addEventListener('change', function() {
        var opcionSeleccionada = dropdown.value;

        // Envía la opción seleccionada al servidor Dash
        fetch('/', {
            method: 'POST',
            body: JSON.stringify({'value': opcionSeleccionada}),
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.text())
        .then(data => {
            // Actualiza el contenido de los contenedores de gráficos
            var graficosSesionesContainer = document.getElementById('graficos-sesiones-container');
            var graficosAusentesContainer = document.getElementById('graficos-ausentes-container');
            graficosSesionesContainer.innerHTML = data.split('<!-- split -->')[0];
            graficosAusentesContainer.innerHTML = data.split('<!-- split -->')[1];
        })
        .catch(error => console.error('Error:', error));
    });
});
