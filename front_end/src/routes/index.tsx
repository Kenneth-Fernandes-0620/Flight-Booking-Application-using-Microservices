import { RouteObject } from "react-router";
import Home from "../pages/Home";
import Layout from "../layout";
import Booking from "../pages/Booking";
import Reservation from "../pages/Reservation";

const routes: RouteObject[] = [
	{
		path: "/",
		element: <Layout />,
		children: [
			{
				children: [
					{
						path: "",						
						element: <Home />,
					},
					{
						path: "booking",
						element: <Booking />,
					},
					{
						path: "reserve",
						element: <Reservation />,
					}
				],
			},
		],
	},
];

export default routes;
