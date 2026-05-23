import { call } from "frappe-ui";
import { defineStore } from "pinia";
import { ref } from "vue";

export interface PortalDoctype {
  doctype_name: string;
  label: string;
  icon: string;
  owner_field: string;
  title_field: string;
  status_field: string;
  date_field: string;
}

export interface PortalMilestone {
  name: string;
  subject: string;
  status: string;
  exp_end_date: string;
  progress: number;
}

export interface PortalTask {
  name: string;
  subject: string;
  status: string;
  progress: number;
  exp_start_date: string;
  exp_end_date: string;
  is_milestone: number;
  milestones: PortalMilestone[];
}

export const usePortalStore = defineStore("portal", () => {
  const portalTitle = ref("Customer Portal");
  const doctypes = ref<PortalDoctype[]>([]);
  const loaded = ref(false);

  // Project tasks sidebar state (shown when on a Project detail)
  const projectTasks = ref<PortalTask[]>([]);
  const loadedTasksFor = ref<string | null>(null);
  const loadingTasks = ref(false);

  // Task milestones sidebar state (shown when on a Task detail)
  const taskMilestones = ref<PortalMilestone[]>([]);
  const loadedMilestonesFor = ref<string | null>(null);
  const loadingMilestones = ref(false);

  async function load() {
    if (loaded.value) return;
    const config = await call("customer_portal.api.portal.get_portal_config");
    portalTitle.value = config.portal_title;
    doctypes.value = config.doctypes;
    loaded.value = true;
  }

  async function loadProjectTasks(projectName: string) {
    if (loadedTasksFor.value === projectName) return;
    loadingTasks.value = true;
    try {
      const tasks = await call("customer_portal.api.portal.get_project_tasks", {
        name: projectName,
      });
      projectTasks.value = tasks || [];
      loadedTasksFor.value = projectName;
    } catch {
      projectTasks.value = [];
      loadedTasksFor.value = null;
    } finally {
      loadingTasks.value = false;
    }
  }

  function clearProjectTasks() {
    projectTasks.value = [];
    loadedTasksFor.value = null;
  }

  async function loadTaskMilestones(taskName: string) {
    if (loadedMilestonesFor.value === taskName) return;
    loadingMilestones.value = true;
    try {
      const milestones = await call("customer_portal.api.portal.get_task_milestones", {
        name: taskName,
      });
      taskMilestones.value = milestones || [];
      loadedMilestonesFor.value = taskName;
    } catch {
      taskMilestones.value = [];
      loadedMilestonesFor.value = null;
    } finally {
      loadingMilestones.value = false;
    }
  }

  function clearTaskMilestones() {
    taskMilestones.value = [];
    loadedMilestonesFor.value = null;
  }

  return {
    portalTitle, doctypes, loaded, load,
    projectTasks, loadingTasks, loadProjectTasks, clearProjectTasks,
    taskMilestones, loadingMilestones, loadTaskMilestones, clearTaskMilestones,
  };
});
