// Initialize charts when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Sample data for the charts
    const trendsData = {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
            label: 'Immigration Applications',
            data: [65000, 72000, 68000, 75000, 82000, 85000],
            borderColor: '#4f46e5',
            backgroundColor: 'rgba(79, 70, 229, 0.1)',
            tension: 0.4,
            fill: true
        }]
    };

    const countriesData = {
        labels: ['Mexico', 'India', 'China', 'Philippines', 'Brazil'],
        datasets: [{
            label: 'Immigrants by Country',
            data: [625000, 425000, 350000, 275000, 225000],
            backgroundColor: [
                'rgba(79, 70, 229, 0.8)',
                'rgba(129, 140, 248, 0.8)',
                'rgba(16, 185, 129, 0.8)',
                'rgba(245, 158, 11, 0.8)',
                'rgba(239, 68, 68, 0.8)'
            ],
            borderWidth: 1
        }]
    };

    // Configure and create the trends chart
    const trendsChart = new Chart(document.getElementById('trendsChart'), {
        type: 'line',
        data: trendsData,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Monthly Immigration Trends'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });

    // Configure and create the countries chart
    const countriesChart = new Chart(document.getElementById('countriesChart'), {
        type: 'doughnut',
        data: countriesData,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right'
                },
                title: {
                    display: true,
                    text: 'Immigration by Country of Origin'
                }
            },
            animation: {
                animateScale: true,
                animateRotate: true,
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });

    // Add interactivity to stats cards
    const statsCards = document.querySelectorAll('.bg-white.rounded-lg.shadow');
    statsCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Add filter functionality
    const filterButtons = document.querySelectorAll('nav button');
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            filterButtons.forEach(btn => btn.classList.remove('text-indigo-600'));
            // Add active class to clicked button
            this.classList.add('text-indigo-600');
            
            // Update charts based on selected filter (to be implemented)
            updateChartsData(this.textContent.toLowerCase());
        });
    });
});

// Function to update charts data based on selected filter
function updateChartsData(filter) {
    // Sample implementation - to be expanded based on real data
    if (filter === 'trends') {
        // Update charts with trends data
        console.log('Updating to trends view');
    } else if (filter === 'reports') {
        // Update charts with reports data
        console.log('Updating to reports view');
    } else {
        // Default to overview
        console.log('Updating to overview');
    }
}

// Add window resize handler for responsive charts
window.addEventListener('resize', function() {
    Chart.instances.forEach(chart => {
        chart.resize();
    });
});

// Add smooth scrolling for navigation
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});