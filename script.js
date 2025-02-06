const labels = [2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034, 2035, 2036, 2037, 2038, 2039, 2040, 2041, 2042, 2043, 2044, 2045, 2046, 2047, 2048, 2049, 2050, 2051, 2052, 2053, 2054, 2055, 2056, 2057, 2058, 2059, 2060, 2061, 2062, 2063, 2064, 2065, 2066, 2067, 2068, 2069, 2070, 2071, 2072, 2073, 2074, 2075, 2076, 2077, 2078, 2079, 2080, 2081, 2082, 2083, 2084, 2085, 2086, 2087, 2088, 2089, 2090, 2091, 2092, 2093, 2094, 2095, 2096, 2097, 2098, 2099, 2100];
const data = [857.1, 661.75, 646.88, 651.85, 511.57, 615.1, 622.98, 750.48, 724.02, 638.05, 780.5, 626.57, 715.49, 750.2, 706.0, 626.36, 909.73, 504.16, 596.37, 597.97, 690.6, 890.36, 558.66, 595.02, 793.28, 782.95, 808.87, 754.19, 591.94, 599.3, 688.07, 678.13, 614.6, 829.69, 695.39, 519.27, 635.44, 703.62, 598.09, 619.78, 675.91, 667.1, 636.42, 725.6, 643.73, 597.53, 527.26, 662.86, 796.23, 607.56, 811.35, 739.08, 581.21, 510.38, 529.5, 558.46, 579.27, 645.71, 539.56, 596.54, 636.3, 773.15, 590.19, 542.91, 686.73, 780.88, 526.25, 591.03, 633.46, 621.71, 427.51, 602.06, 707.02, 385.6, 651.69, 839.45, 533.28, 806.01, 554.87, 622.49, 499.48, 469.14, 496.01, 664.02, 634.32, 536.58, 839.24, 554.34, 549.53, 582.22, 413.74, 417.97, 486.46, 653.81, 639.8];

let myChartHorizontal;
let myChartVertical;

// Crear gráfico horizontal
function createChartHorizontal() {
    const config = {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Mitjana de Precipitació anual',
                data: data,
                backgroundColor: 'rgba(33, 150, 243, 0.2)',
                borderColor: 'rgba(33, 150, 243, 1)',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    beginAtZero: true
                }
            }
        }
    };

    const chartContainer = document.getElementById('graficoBarrasHorizontal').getContext('2d');
    if (myChartHorizontal) {
        myChartHorizontal.destroy(); // Eliminar el gráfico existente
    }

    myChartHorizontal = new Chart(chartContainer, config);
}

// Crear gráfico vertical
function createChartVertical() {
    const config = {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Mitjana de Precipitació anual',
                data: data,
                backgroundColor: 'rgba(33, 150, 243, 0.2)',
                borderColor: 'rgba(33, 150, 243, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    };

    const chartContainer = document.getElementById('graficoBarrasVerticalCanvas').getContext('2d');
    if (myChartVertical) {
        myChartVertical.destroy(); // Eliminar el gráfico existente
    }

    myChartVertical = new Chart(chartContainer, config);
}

// Alternar entre los gráficos
function toggleGraphs() {
    const horizontalContainer = document.getElementById('graficoHorizontalContainer');
    const verticalContainer = document.getElementById('graficoBarrasVertical');
    
    // Alternar visibilidad
    if (horizontalContainer.style.display === 'none') {
        horizontalContainer.style.display = 'block';
        verticalContainer.style.display = 'none';
        createChartHorizontal();
    } else {
        horizontalContainer.style.display = 'none';
        verticalContainer.style.display = 'block';
        createChartVertical();
    }
}

// Cambiar el tamaño del gráfico al hacer clic sobre él
document.getElementById('graficoHorizontalContainer').addEventListener('click', () => {
    const chartContainer = document.getElementById('graficoHorizontalContainer');
    if (chartContainer.style.height === '1500px') {
        chartContainer.style.height = '400px'; // Tamaño normal
    } else {
        chartContainer.style.height = '1500px'; // Tamaño extendido
    }

    // Volver a renderizar el gráfico con el nuevo tamaño
    myChartHorizontal.resize();
});

// Mostrar el gráfico horizontal por defecto
window.onload = function() {
    createChartHorizontal();
};
