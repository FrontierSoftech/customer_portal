<template>
  <div class="flex flex-col h-full overflow-hidden">

    <!-- ── Header bar ─────────────────────────────────────────────── -->
    <div class="flex items-center justify-between px-3 sm:px-5 h-[42px] border-b border-outline-gray-modals bg-surface-white flex-shrink-0">
      <!-- Breadcrumb: "Label / List ▾" -->
      <div class="flex items-center gap-1 text-sm select-none min-w-0 mr-2">
        <span class="text-ink-gray-5 font-medium truncate max-w-[80px] sm:max-w-none">{{ config?.label || doctypeName }}</span>
        <span class="text-ink-gray-3 mx-0.5">/</span>
        <Popover placement="bottom-start">
          <template #target="{ togglePopover, isOpen }">
            <button
              class="flex items-center gap-0.5 font-semibold text-ink-gray-9 hover:text-ink-gray-7 transition-colors"
              @click="togglePopover"
            >
              List
              <FeatherIcon :name="isOpen ? 'chevron-up' : 'chevron-down'" class="w-3 h-3 text-ink-gray-4 mt-px" />
            </button>
          </template>
          <template #body="{ close }">
            <div class="my-1 rounded-lg border border-outline-gray-modals bg-surface-white shadow-xl min-w-[180px] py-1">
              <div class="px-3 py-1 text-xs font-semibold text-ink-gray-4 uppercase tracking-wider">
                Default Views
              </div>
              <button
                class="w-full flex items-center gap-2 px-3 py-1.5 text-sm text-ink-gray-7 hover:bg-surface-gray-2 transition-colors"
                @click="close"
              >
                <FeatherIcon name="align-justify" class="w-3.5 h-3.5 text-ink-gray-5" />
                List View
              </button>
              <div class="border-t border-outline-gray-modals my-1"></div>
              <button
                class="w-full flex items-center gap-2 px-3 py-1.5 text-sm text-ink-gray-7 hover:bg-surface-gray-2 transition-colors"
                @click="close"
              >
                <FeatherIcon name="plus" class="w-3.5 h-3.5 text-ink-gray-5" />
                Create View
              </button>
            </div>
          </template>
        </Popover>
      </div>

      <!-- Action buttons -->
      <div class="flex items-center gap-1.5">
        <!-- Refresh -->
        <button
          class="flex items-center justify-center w-7 h-7 rounded hover:bg-surface-gray-2 text-ink-gray-5 hover:text-ink-gray-9 transition-colors disabled:opacity-40"
          :disabled="loading"
          title="Refresh"
          @click="refresh"
        >
          <FeatherIcon name="refresh-cw" class="w-3.5 h-3.5" :class="loading && 'animate-spin'" />
        </button>

        <!-- Filter popover (always visible) -->
        <FilterPopover
          :fields="listFields"
          @change="onFilterChange"
        />

        <!-- Sort popover (desktop only) -->
        <SortPopover
          class="hidden sm:flex"
          :fields="listFields"
          @change="onSortChange"
        />

        <!-- Columns popover (desktop only) -->
        <ColumnsPopover
          class="hidden sm:flex"
          :columns="columns"
          :all-fields="listFields"
          :default-columns="defaultColumns"
          @update:columns="onColumnsChange"
        />
      </div>
    </div>

    <!-- ── Loading (first load, no rows yet) ─────────────────────── -->
    <div v-if="loading && records.length === 0" class="flex-1 flex items-center justify-center">
      <div class="animate-spin rounded-full h-7 w-7 border-b-2 border-blue-500"></div>
    </div>

    <!-- ── List view ─────────────────────────────────────────────── -->
    <template v-else>
      <!-- Empty state -->
      <div
        v-if="records.length === 0"
        class="flex-1 flex flex-col items-center justify-center gap-2 text-ink-gray-4"
      >
        <FeatherIcon name="inbox" class="w-10 h-10" />
        <p class="text-sm font-medium text-ink-gray-6">No records found</p>
        <p v-if="Object.keys(activeFilters).length" class="text-xs text-ink-gray-4">
          Try adjusting your filters
        </p>
      </div>

      <template v-else>
        <!-- frappe-ui ListView -->
        <ListView
          :columns="columns"
          :rows="records"
          row-key="name"
          :options="{
            selectable: false,
            showTooltip: false,
            getRowRoute: (row) => ({
              name: 'RecordDetail',
              params: { doctypeName, name: row.name },
            }),
          }"
          class="flex-1"
        >
          <template #default>
            <!-- Column headers -->
            <ListHeader class="sm:mx-5 mx-3 rounded">
              <ListHeaderItem
                v-for="col in columns"
                :key="col.key"
                :item="col"
              />
            </ListHeader>

            <!-- Rows -->
            <ListRows class="sm:mx-5 mx-3">
              <ListRow
                v-for="row in records"
                :key="row.name"
                :row="row"
                v-slot="{ column, item }"
                class="truncate text-sm"
              >
                <!-- Status column → colored dot + text -->
                <template v-if="column.key === statusField && statusField">
                  <div class="flex items-center gap-1.5">
                    <span
                      v-if="isOpenStatus(item)"
                      class="relative flex-shrink-0 w-3.5 h-3.5 rounded-full border-2 border-blue-500 flex items-center justify-center"
                    >
                      <span class="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
                    </span>
                    <span
                      v-else
                      :class="['flex-shrink-0 w-3.5 h-3.5 rounded-full', statusDotBg(item)]"
                    ></span>
                    <span :class="['text-xs font-medium', statusTextColor(item)]">{{ item || '—' }}</span>
                  </div>
                </template>

                <!-- Date / Datetime columns → relative time -->
                <span
                  v-else-if="column.key === 'creation' || column.key === 'modified'"
                  class="text-ink-gray-5 text-xs"
                >
                  {{ relativeTime(item) }}
                </span>

                <!-- Title / fallback -->
                <span
                  v-else
                  class="truncate"
                  :class="column.key === titleField ? 'font-medium text-ink-gray-9' : 'text-ink-gray-6'"
                >
                  {{ item || '—' }}
                </span>
              </ListRow>
            </ListRows>
          </template>
        </ListView>

        <!-- ── Footer (pagination) ────────────────────────────────── -->
        <div class="border-t border-outline-gray-modals px-5 py-2 flex-shrink-0 bg-surface-white">
          <ListFooter
            v-model="pageLength"
            :options="{
              rowCount: records.length + start,
              totalCount: totalCount,
              pageLengthOptions: [20, 50, 100],
            }"
            @loadMore="loadMore"
            @update:modelValue="onPageLengthChange"
          />
        </div>
      </template>
    </template>
  </div>
</template>

<script setup lang="ts">
import {
  call,
  FeatherIcon,
  ListFooter,
  ListHeader,
  ListHeaderItem,
  ListRow,
  ListRows,
  ListView,
  Popover,
} from "frappe-ui";
import { computed, onMounted, ref, watch } from "vue";
import { usePortalStore } from "../stores/portal";
import ColumnsPopover from "../components/view-controls/ColumnsPopover.vue";
import FilterPopover from "../components/view-controls/FilterPopover.vue";
import SortPopover from "../components/view-controls/SortPopover.vue";

const props = defineProps<{ doctypeName: string }>();
const portalStore = usePortalStore();

// ── State ──────────────────────────────────────────────────────────
const loading = ref(false);
const records = ref<any[]>([]);
const titleField = ref("name");
const statusField = ref("");
const totalCount = ref(0);
const pageLength = ref(20);
const start = ref(0);

const activeFilters = ref<Record<string, any>>({});
const orderBy = ref("modified desc");

// Fields for filter / sort / columns popovers
const listFields = ref<any[]>([]);

// ── Config ─────────────────────────────────────────────────────────
const config = computed(() =>
  portalStore.doctypes.find((d) => d.doctype_name === props.doctypeName)
);

// ── Columns ────────────────────────────────────────────────────────
const defaultColumns = computed<any[]>(() => {
  const cols: any[] = [
    { key: "name", label: "ID", width: "7rem" },
    { key: titleField.value, label: "Subject", width: "16rem" },
  ];
  if (statusField.value) cols.push({ key: statusField.value, label: "Status", width: "9rem" });
  cols.push({ key: "creation", label: "Created", width: "8rem" });
  return cols;
});

const columns = ref<any[]>([]);

// ── localStorage helpers ───────────────────────────────────────────
function storageKey(dt: string) { return `cp_cols_${dt}`; }

function persistColumns(cols: any[]) {
  try { localStorage.setItem(storageKey(props.doctypeName), JSON.stringify(cols)); } catch {}
}

function loadPersistedColumns(): any[] | null {
  try {
    const raw = localStorage.getItem(storageKey(props.doctypeName));
    if (!raw) return null;
    const parsed: any[] = JSON.parse(raw);
    // Normalise: replace any old %-based widths with rem so mobile scroll works
    const normalised = parsed.map((c) =>
      c.width?.endsWith("%") ? { ...c, width: "10rem" } : c
    );
    // If saved columns don't include ID as first column, discard and use new default
    if (normalised[0]?.key !== "name") return null;
    return normalised;
  } catch { return null; }
}

function syncDefaultColumns() {
  if (columns.value.length === 0) {
    columns.value = loadPersistedColumns() ?? [...defaultColumns.value];
  }
}

// ── Status helpers ─────────────────────────────────────────────────
const OPEN_KW = ["open", "awaiting", "in progress", "active", "pending", "replied", "new"];
const CLOSED_KW = ["closed", "resolved", "completed", "done", "fulfilled"];
const DANGER_KW = ["overdue", "failed", "rejected", "expired", "cancelled"];
const HOLD_KW = ["hold", "paused", "waiting"];

function isOpenStatus(s: string) { const l = (s || "").toLowerCase(); return OPEN_KW.some(k => l.includes(k)); }
function statusDotBg(s: string) {
  const l = (s || "").toLowerCase();
  if (CLOSED_KW.some(k => l.includes(k))) return "bg-gray-400";
  if (DANGER_KW.some(k => l.includes(k))) return "bg-red-500";
  if (HOLD_KW.some(k => l.includes(k))) return "bg-orange-400";
  return "bg-gray-400";
}
function statusTextColor(s: string) {
  const l = (s || "").toLowerCase();
  if (OPEN_KW.some(k => l.includes(k))) return "text-blue-700";
  if (CLOSED_KW.some(k => l.includes(k))) return "text-gray-500";
  if (DANGER_KW.some(k => l.includes(k))) return "text-red-700";
  if (HOLD_KW.some(k => l.includes(k))) return "text-orange-700";
  return "text-gray-500";
}

// ── Date format ────────────────────────────────────────────────────
function relativeTime(d: string): string {
  if (!d) return "—";
  return new Date(d).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

// ── Data fetching ──────────────────────────────────────────────────
async function fetchListFields() {
  try {
    const fields = await call("customer_portal.api.portal.get_list_fields", {
      doctype_name: props.doctypeName,
    });
    listFields.value = fields || [];
  } catch (e) {
    console.error(e);
  }
}

async function fetchRecords(reset = false) {
  if (reset) { start.value = 0; records.value = []; }
  loading.value = true;
  try {
    await portalStore.load();

    // Collect any extra column keys the user has added beyond the defaults
    const defaultKeys = new Set(["name", "creation", "modified", titleField.value, statusField.value].filter(Boolean));
    const extraKeys = columns.value.map((c) => c.key).filter((k) => k && !defaultKeys.has(k));

    const res = await call("customer_portal.api.portal.get_records", {
      doctype_name: props.doctypeName,
      page_length: pageLength.value,
      start: start.value,
      order_by: orderBy.value,
      field_filters: Object.keys(activeFilters.value).length
        ? JSON.stringify(activeFilters.value)
        : null,
      extra_fields: extraKeys.length ? JSON.stringify(extraKeys) : null,
    });
    const fetched = res.records || [];
    if (reset || start.value === 0) {
      records.value = fetched;
    } else {
      records.value = [...records.value, ...fetched];
    }
    titleField.value = res.title_field || "name";
    statusField.value = res.status_field || "";
    totalCount.value = res.total_count ?? fetched.length;
    syncDefaultColumns();
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
}

function refresh() {
  activeFilters.value = {};
  orderBy.value = "modified desc";
  // Keep user column customisation — only reset filters/sort
  fetchRecords(true);
}

function loadMore() {
  start.value = records.value.length;
  fetchRecords(false);
}

function onPageLengthChange(count: number) {
  pageLength.value = count;
  fetchRecords(true);
}

// ── View-control handlers ──────────────────────────────────────────
function onFilterChange(filters: Record<string, any>) {
  activeFilters.value = filters;
  fetchRecords(true);
}

function onSortChange(ob: string) {
  orderBy.value = ob;
  fetchRecords(true);
}

function onColumnsChange(cols: any[]) {
  columns.value = cols;
  persistColumns(cols);
  // Re-fetch if a newly added column's data isn't already in the records
  if (records.value.length > 0) {
    const fetched = Object.keys(records.value[0]);
    const missing = cols.some((c) => c.key && !fetched.includes(c.key));
    if (missing) fetchRecords(true);
  }
}

// ── Lifecycle ──────────────────────────────────────────────────────
onMounted(async () => {
  await Promise.all([fetchRecords(true), fetchListFields()]);
});

watch(() => props.doctypeName, async () => {
  activeFilters.value = {};
  orderBy.value = "modified desc";
  pageLength.value = 20;
  start.value = 0;
  columns.value = [];           // triggers loadPersistedColumns() in syncDefaultColumns
  await Promise.all([fetchRecords(true), fetchListFields()]);
});
</script>
