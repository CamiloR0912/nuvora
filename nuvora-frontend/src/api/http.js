import axios from "axios";

export const http = axios.create({
  baseURL: "/api",
});

http.interceptors.request.use((config) => {
  const token = localStorage.getItem("token"); // guardarás esto al hacer login
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default http;