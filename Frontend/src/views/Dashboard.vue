<template>
    <div class="dashboard-container">
        <div v-if="loading" class="loading-spinner">
            <div class="spinner"></div>
            <p>Loading HR Analytics...</p>
        </div>

        <div v-if="!loading && analyticsData">
            <!-- KPI Cards -->
            <div class="kpi-grid">
                <div class="kpi-card">
                    <h3>Total Employees</h3>
                    <p>{{ analyticsData.turnover_metrics.headcount }}</p>
                </div>
                <div class="kpi-card">
                    <h3>Turnover Rate</h3>
                    <p>{{ analyticsData.turnover_metrics.turnover_rate }}%</p>
                </div>
                <div class="kpi-card">
                    <h3>Average Salary</h3>
                    <p>${{ analyticsData.payroll_compensation.overall.avg.toLocaleString() }}</p>
                </div>
            </div>

            <!-- Charts -->
            <div class="chart-grid">
                <div class="chart-card">
                    <h3>Workforce Composition</h3>
                    <Doughnut :data="workforceCompositionData" :options="chartOptions" />
                </div>
                <div class="chart-card">
                    <h3>Tenure Distribution</h3>
                    <Bar :data="tenureDistributionData" :options="chartOptions" />
                </div>
                <div class="chart-card">
                    <h3>Absence Rate by Department</h3>
                    <Bar :data="absenceRateByDeptData" :options="chartOptions" />
                </div>
                <div class="chart-card">
                    <h3>Performance vs. Compensation</h3>
                    <Scatter :data="performanceVsCompensationData" :options="scatterChartOptions" />
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { Bar, Doughnut, Scatter } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement, PointElement } from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement, PointElement);

const loading = ref(true);
const analyticsData = ref(null);

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'bottom',
            labels: {
                font: {
                    size: 11
                },
                padding: 15
            }
        },
    },
    layout: {
        padding: 30
    },
    scales: {
        x: {
            ticks: {
                font: {
                    size: 11
                }
            }
        },
        y: {
            ticks: {
                font: {
                    size: 11
                }
            }
        }
    }
};

const scatterChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'bottom',
            labels: {
                font: {
                    size: 11
                },
                padding: 15
            }
        },
    },
    layout: {
        padding: 30
    },
    scales: {
        x: {
            type: 'linear',
            position: 'bottom',
            title: {
                display: true,
                text: 'Performance Score',
                font: {
                    size: 12
                }
            },
            ticks: {
                font: {
                    size: 11
                }
            }
        },
        y: {
            title: {
                display: true,
                text: 'Compensation (Salary)',
                font: {
                    size: 12
                }
            },
            ticks: {
                font: {
                    size: 11
                }
            }
        }
    }
};


async function fetchAnalyticsData() {
    try {
        const response = await fetch('http://127.0.0.1:5002/api/hr-analytics-summary');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        analyticsData.value = await response.json();
    } catch (error) {
        console.error('Error fetching HR analytics data:', error);
    } finally {
        loading.value = false;
    }
}

onMounted(() => {
    fetchAnalyticsData();
});

const workforceCompositionData = computed(() => ({
    labels: analyticsData.value?.workforce_composition.by_department.map(d => d.dept),
    datasets: [
        {
            backgroundColor: ['#41B883', '#E46651', '#00D8FF', '#DD1B16', '#FFC107', '#3F51B5'],
            data: analyticsData.value?.workforce_composition.by_department.map(d => d.headcount),
        },
    ],
}));

const tenureDistributionData = computed(() => ({
    labels: Object.keys(analyticsData.value?.tenure_distribution.tenure_brackets || {}),
    datasets: [
        {
            label: 'Number of Employees',
            backgroundColor: '#41B883',
            data: Object.values(analyticsData.value?.tenure_distribution.tenure_brackets || {}),
        },
    ],
}));

const absenceRateByDeptData = computed(() => ({
    labels: analyticsData.value?.attendance_patterns.dept_absence_rates.map(d => d.dept),
    datasets: [
        {
            label: 'Absence Rate (%)',
            backgroundColor: '#E46651',
            data: analyticsData.value?.attendance_patterns.dept_absence_rates.map(d => d.rate),
        },
    ],
}));

const performanceVsCompensationData = computed(() => ({
    datasets: [
        {
            label: 'Employee Performance vs. Compensation',
            backgroundColor: '#3F51B5',
            data: analyticsData.value?.performance_vs_compensation.map(d => ({ x: d.performance, y: d.compensation })),
        },
    ],
}));

</script>

<style scoped>
.dashboard-container {
    padding: 2rem;
    background-color: #f0f2f5;
}

.loading-spinner {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 80vh;
}

.spinner {
    border: 4px solid rgba(0, 0, 0, 0.1);
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border-left-color: #41B883;
    animation: spin 1s ease infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.chart-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
}

.kpi-card, .chart-card {
    background: #fff;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s;
}

.kpi-card:hover, .chart-card:hover {
    transform: translateY(-5px);
}

.kpi-card {
    text-align: center;
}

.kpi-card h3 {
    margin-bottom: 0.5rem;
    color: #333;
}

.kpi-card p {
    font-size: 2rem;
    font-weight: bold;
    color: #41B883;
}

.chart-card {
    height: 465px;
}

.chart-card h3 {
    margin-bottom: 1rem;
    text-align: center;
}
</style>
