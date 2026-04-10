import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem("refresh_token");
      if (refreshToken) {
        try {
          const res = await axios.post(`${API_BASE}/api/v1/auth/refresh`, {
            refresh_token: refreshToken,
          });
          const { access_token, refresh_token } = res.data;
          localStorage.setItem("access_token", access_token);
          localStorage.setItem("refresh_token", refresh_token);
          apiClient.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
          originalRequest.headers["Authorization"] = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        } catch {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data: { email: string; password: string; full_name: string; role?: string }) =>
    apiClient.post("/api/v1/auth/register", data),
  login: (data: { email: string; password: string }) =>
    apiClient.post("/api/v1/auth/login", data),
  me: () => apiClient.get("/api/v1/auth/me"),
};

// Fields API
export const fieldsAPI = {
  list: () => apiClient.get("/api/v1/fields"),
  create: (data: any) => apiClient.post("/api/v1/fields", data),
  get: (id: string) => apiClient.get(`/api/v1/fields/${id}`),
  update: (id: string, data: any) => apiClient.put(`/api/v1/fields/${id}`, data),
  delete: (id: string) => apiClient.delete(`/api/v1/fields/${id}`),
};

// Satellite API
export const satelliteAPI = {
  getNDVI: (fieldId: string, months?: number) =>
    apiClient.get(`/api/v1/satellite/ndvi/${fieldId}`, { params: { months } }),
  getImage: (fieldId: string) => apiClient.get(`/api/v1/satellite/image/${fieldId}`),
  fetch: (fieldId: string) => apiClient.post(`/api/v1/satellite/fetch/${fieldId}`),
};

// Carbon API
export const carbonAPI = {
  listCredits: () => apiClient.get("/api/v1/carbon/credits"),
  getSummary: () => apiClient.get("/api/v1/carbon/credits/summary"),
  getCredit: (id: string) => apiClient.get(`/api/v1/carbon/credits/${id}`),
  calculate: (data: { field_id: string; year: number }) =>
    apiClient.post("/api/v1/carbon/calculate", data),
  listOnMarketplace: (creditId: string, data: { price_per_ton: number; tons_to_list?: number }) =>
    apiClient.post(`/api/v1/carbon/credits/${creditId}/list`, data),
};

// Reports API
export const reportsAPI = {
  generate: (data: any) => apiClient.post("/api/v1/reports/generate", data),
  get: (id: string) => apiClient.get(`/api/v1/reports/${id}`),
  download: (id: string) =>
    apiClient.get(`/api/v1/reports/${id}/download`, { responseType: "blob" }),
  listByField: (fieldId: string) => apiClient.get(`/api/v1/reports/field/${fieldId}`),
};

// Sensors API
export const sensorsAPI = {
  list: () => apiClient.get("/api/v1/sensors"),
  create: (data: any) => apiClient.post("/api/v1/sensors", data),
  getReadings: (sensorId: string, days?: number) =>
    apiClient.get(`/api/v1/sensors/${sensorId}/readings`, { params: { days } }),
  getLatest: (sensorId: string) => apiClient.get(`/api/v1/sensors/${sensorId}/latest`),
};

// Marketplace API
export const marketplaceAPI = {
  list: (params?: { min_price?: number; max_price?: number; page?: number }) =>
    apiClient.get("/api/v1/marketplace", { params }),
  get: (id: string) => apiClient.get(`/api/v1/marketplace/${id}`),
  buy: (listingId: string, data: { tons_to_buy: number }) =>
    apiClient.post(`/api/v1/marketplace/${listingId}/buy`, data),
  myListings: () => apiClient.get("/api/v1/marketplace/my/listings"),
  myTransactions: () => apiClient.get("/api/v1/marketplace/my/transactions"),
};
