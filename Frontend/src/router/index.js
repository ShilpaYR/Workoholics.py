import { createRouter, createWebHistory } from 'vue-router';
import JobList from '../views/JobList.vue';
import CreateJob from '../views/CreateJob.vue';
import CareerPage from '../views/CareerPage.vue';
import Home from '../views/Home.vue';
import Employees from '../views/Employees.vue';
import ContactUs from '../views/ContactUs.vue';
import Dashboard from '../views/Dashboard.vue';
import EmployeeDashboard from '../views/EmployeeDashboard.vue';
import Queries from '../views/Queries.vue';
import Setup2FA from '../views/Setup2FA.vue';
import Verify2FA from '../views/Verify2FA.vue';
import { store } from '../store.js';

const routes = [
  {
    path: '/job-list',
    name: 'JobList',
    component: JobList,
    meta: { requiresAuth: true, allowedRoles: ['Applicant', 'HRMgr'] }
  },
  {
    path: '/create',
    name: 'CreateJob',
    component: CreateJob,
    meta: { requiresAuth: true, requiredRole: 'HRMgr' }
  },
  {
    path: '/',
    name: 'Home',
    component: Home,
  },
  {
    path: '/employees',
    name: 'Employees',
    component: Employees,
  },
  {
    path: '/career-page',
    name: 'CareerPage',
    component: CareerPage,
  },
  {
    path: '/contact-us',
    name: 'ContactUs',
    component: ContactUs,
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true, requiredRole: 'HRMgr' }
  },
  {
    path: '/employee-dashboard',
    name: 'EmployeeDashboard',
    component: EmployeeDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/queries',
    name: 'Queries',
    component: Queries,
    meta: { requiresAuth: true }
  },
  {
    path: '/setup-2fa',
    name: 'Setup2FA',
    component: Setup2FA,
  },
  {
    path: '/verify-2fa',
    name: 'Verify2FA',
    component: Verify2FA,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const loggedIn = store.user;

  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!loggedIn) {
      next({ name: 'Employees' });
    } else {
      const requiredRole = to.meta.requiredRole;
      if (requiredRole && store.user.role !== requiredRole) {
        next({ name: 'EmployeeDashboard' });
      } else {
        const allowedRoles = to.meta.allowedRoles;
        if (allowedRoles && !allowedRoles.includes(store.user.role)) {
          next({ name: 'Dashboard' }); 
        } else {
          next();
        }
      }
    }
  } else {
    next();
  }
});

export default router;
