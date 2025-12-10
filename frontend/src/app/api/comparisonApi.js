import axios from "axios";


const API_URL = `${process.env.NEXT_PUBLIC_BACKEND_END_POINT}/comparison/`;

export const getToxicity = async ({ board_name, start_date, end_date } = {}) => {
    const params = {};

    if (board_name) params.board_name = board_name;
    if (start_date) params.start_date = start_date;
    if (end_date) params.end_date = end_date;

    const { data } = await axios.get(API_URL + "top-toxic", { params });
    return data;
};
