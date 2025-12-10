import axios from "axios";

const API_URL = `${process.env.NEXT_PUBLIC_BACKEND_END_POINT}/reddit/`;

export const getSummaryStats = async () => {
  const { data } = await axios.get(API_URL + "stats/summary");
  return data;
};

export const getDailyPostsCount = async () => {
  const { data } = await axios.get(API_URL + "posts/daily-counts");
  return data;
};

export const getTopSubscribers = async () => {
  const { data } = await axios.get(API_URL + "subreddit/top-subscribers");
  return data;
};
