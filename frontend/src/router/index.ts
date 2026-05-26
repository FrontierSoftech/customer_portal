import { createRouter, createWebHistory } from "vue-router";

export const router = createRouter({
  history: createWebHistory("/portal/"),
  routes: [
    {
      path: "/",
      component: () => import("../layouts/MainLayout.vue"),
      children: [
        { path: "", redirect: "/records" },
        {
          path: "records",
          name: "RecordListDefault",
          component: () => import("../pages/SelectDoctype.vue"),
        },
        {
          path: "records/:doctypeName",
          name: "RecordList",
          component: () => import("../pages/RecordList.vue"),
          props: true,
        },
        {
          path: "records/:doctypeName/:name",
          name: "RecordDetail",
          component: () => import("../pages/RecordDetail.vue"),
          props: true,
        },
      ],
    },
    {
      path: "/:pathMatch(.*)*",
      redirect: "/",
    },
  ],
});

router.beforeEach(async (to, _, next) => {
  const { useAuthStore } = await import("../stores/auth");
  const authStore = useAuthStore();
  if (!authStore.isLoggedIn) {
    window.location.href = "/login?redirect-to=/portal";
    return;
  }
  next();
});
