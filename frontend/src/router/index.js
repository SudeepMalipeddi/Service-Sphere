import { createRouter, createWebHistory } from 'vue-router'
import { getUserRole, isAuthenticated } from '@/utils/authutils'


import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/auth/LoginView.vue'
import RegisterView from '@/views/auth/RegisterView.vue'
import AdminDashboardView from '@/views/admin/DashboardView.vue'
import AdminServiceManagementView from '@/views/admin/AdminServiceManagementView.vue'
import AdminCustomersView from '@/views/admin/CustomerView.vue'
import AdminProfessionalsView from '@/views/admin/ProfessionalsView.vue'
import ProfessionalProfileView from "@/views/professional/ProfileView.vue"
import ProfessionalDashboardView from "@/views/professional/DashboardView.vue"
import NotificationsView from '@/views/NotificationsView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: { requiresGuest: true }
  },
  {
    path: '/notifications',
    name: 'notifications',
    component: NotificationsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'admin-dashboard',
    component: AdminDashboardView,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/customers',
    name: 'admin-customers',
    component: AdminCustomersView,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/professionals',
    name: 'admin-professionals',
    component: AdminProfessionalsView,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/services',
    name: 'admin-services',
    component: AdminServiceManagementView,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/professional',
    name: 'professional-dashboard',
    component: ProfessionalDashboardView,
    meta: { requiresAuth: true, role: 'professional' }
  },
  {
    path: '/professional/profile',
    name: 'professional-profile',
    component: ProfessionalProfileView,
    meta: { requiresAuth: true, role: 'professional' }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: { name: 'home' }
  }
]
const router = createRouter({
  history: createWebHistory(),
  routes
})

// router.beforeEach((to, from, next) => {
//   // Check if route requires authentication
//   if (to.meta.requiresAuth && !isAuthenticated()) {
//     return next({ name: 'login' })
//   }

//   // Check if route requires guest access
//   if (to.meta.requiresGuest && isAuthenticated()) {
//     const role = getUserRole()

//     // Redirect to appropriate dashboard based on role
//     if (role === 'admin') {
//       return next({ name: 'admin-dashboard' })
//     } else if (role === 'customer') {
//       return next({ name: 'customer-dashboard' })
//     } else if (role === 'professional') {
//       return next({ name: 'professional-dashboard' })
//     }

//     return next({ name: 'home' })
//   }

//   // Check if route requires specific role
//   if (to.meta.role && getUserRole() !== to.meta.role) {
//     // Redirect to home if user doesn't have required role
//     return next({ name: 'home' })
//   }

//   next()
// })

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('accessToken');

  if (to.meta.requiresAuth && !token) {
    return next({ name: 'login' });
  }

  if (to.meta.requiresGuest && token) {
    const role = getUserRole();
    if (role === 'admin') {
      return next({ name: 'admin-dashboard' });
    } else if (role === 'customer') {
      return next({ name: 'customer-dashboard' });
    } else if (role === 'professional') {
      return next({ name: 'professional-dashboard' });
    }
    return next({ name: 'home' });
  }

  next();
});

export default router