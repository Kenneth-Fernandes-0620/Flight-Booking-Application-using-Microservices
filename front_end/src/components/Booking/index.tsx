import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Dropdown, { DropdownType } from "./dropdown";

// TODO: Add Price
type ReponseObject = {
	id: string;
	available_seats: number;
	class: string;
	date: string;
	destination: string;
	source: string;
	cost: number
};


function validate(source: string, destination: string, date: string): boolean {
	console.log(date)
	if (source === 'Source' || destination === 'Destination' || date === '')
		return false;

	return true;
}


const toLowerCase = (str: string): string => {
	return str.charAt(0).toLowerCase() + str.slice(1).toLowerCase();
}

const toSentenceCase = (str: string): string => {
	return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}


const BookingHero = () => {

	const [sources, setSources] = useState<string[]>([]);
	const [destinations, setDestinations] = useState<string[]>([]);

	const [source, setSource] = useState<string>('Source');
	const [destination, setDestination] = useState<string>('Destination');
	const [date, setDate] = useState<string>(new Date().toISOString().split("T")[0]);
	const [amount, setAmount] = useState<string>('1');

	const [results, setResults] = useState<ReponseObject[]>([]);
	const [filterSearchText, setFilterSearchText] = useState<string>('Adjust Search Filters to show More Flights');
	const [filteredResults, setFilteredResults] = useState<ReponseObject[]>([]);

	const [sourceDropdown, setSourceDropdown] = useState(false);
	const [destinationDropdown, setDestinationDropdown] = useState(false);
	const [dateDropdown, setDateDropdown] = useState(false);
	const [amountDropdown, setAmountDropdown] = useState(false);
	const [searchFilters, setSearchFilters] = useState<boolean>(false);

	const navigate = useNavigate();

	useEffect(() => {
		// Fetch sources and destinations from the API
		fetch('http://localhost:9000/route/listing/getbookings', {
			method: 'GET',
			redirect: 'follow',
		}).then((response) => {
			return response.json()
		}).then((data: ReponseObject[]) => {
			const tempSources = new Set<string>();
			const tempDestinations = new Set<string>();

			if (data.length > 0) {
				data.forEach((booking) => {
					tempSources.add(toSentenceCase(booking.source));
					tempDestinations.add(toSentenceCase(booking.destination));
				});
			} else {
				setFilterSearchText('No Flights Available');
			}
			setResults(data);
			setSources(Array.from(tempSources));
			setDestinations(Array.from(tempDestinations));
		}).catch((error) => {
			console.error(error);
		});
	}, []);

	useEffect(() => {
		if (!searchFilters)
			return;


		// change the result array
		const filteredResults = results.filter((booking) => {
			const temp_date = booking.date.split('/');
			const modifiedDate = `${temp_date[2]}-${temp_date[1]}-${temp_date[0]}`
			const temp_source = toLowerCase(source);
			const temp_destination = toLowerCase(destination);
			return booking.source === temp_source && booking.destination === temp_destination && modifiedDate === date;
		});

		if (filteredResults.length === 0) {
			setFilterSearchText('No Flights Available');
		}

		setFilteredResults(filteredResults.slice(0, 5));
		console.log(filteredResults);

		setSearchFilters(false);
	}, [searchFilters]);


	const toggleSourceDropdown = () => {
		setSourceDropdown(!sourceDropdown);
	};

	const toggleDestinationDropdown = () => {
		setDestinationDropdown(!destinationDropdown);
	};

	const toggleDateDropdown = () => {
		setDateDropdown(!dateDropdown);
	};

	const toggleAmountDropdown = () => {
		setAmountDropdown(!amountDropdown);
	};

	const beginSearch = () => {
		if (!validate(source, destination, date)) {
			alert('Please fill all the fields');
			return;
		}

		setSearchFilters(true);
	}


	return (
		<div className="hero z-[1] w-full h-[100vh] grid place-items-center bg-[#141b2b] relative">
			<div className="flex md:flex-row flex-col items-center w-full md:px-[200px] px-8 justify-between md:gap-0 gap-28">

				<div className="container mx-auto border border-blue-400 flex-1 flex flex-col rounded-lg md:px-[50px] px-8 md:py-[25px]">
					{/* Searching Parameters */}
					<div className="container mx-auto grid grid-cols-[1fr,1fr,1fr,100px,150px] gap-4">

						<Dropdown dropdown={sourceDropdown} toggleDropdown={toggleSourceDropdown} defaultValue={source} updateValue={setSource} options={sources} dropDownType={DropdownType.TEXT} />
						<Dropdown dropdown={destinationDropdown} toggleDropdown={toggleDestinationDropdown} defaultValue={destination} updateValue={setDestination} options={destinations} dropDownType={DropdownType.TEXT} />
						<Dropdown dropdown={dateDropdown} toggleDropdown={toggleDateDropdown} defaultValue={date} updateValue={setDate} options={[]} dropDownType={DropdownType.DATE} />
						<Dropdown dropdown={amountDropdown} toggleDropdown={toggleAmountDropdown} defaultValue={amount} updateValue={setAmount} options={[]} dropDownType={DropdownType.NUMBER} />
						<button className="bg-blue-400 rounded-full text-gray-900 px-6 py-2 font-semibold hover:bg-gray-700 hover:text-white"
							onClick={beginSearch}
						>
							Search
						</button>

					</div>
					{/* Display Available Flight Bookings */}
					<div className="min-h-[50vh] border border-black bg-[#60A5FA44] flex flex-col flex-1 rounded-lg mt-3 px-2 py-2">
						<span className="text-white text-[28px] text-sm">
							Select Flight
						</span>
						{
							filteredResults.length > 0 ?
								filteredResults.map((booking) => {
									return (
										<div key={booking.id} className="flex flex-row justify-between items-center border border-black bg-[#fff] px-2 py-1 rounded-lg mt-2">
											<div>
												<span className="text-black font-semibold">Departure: </span>
												<span className="text-black">{toSentenceCase(booking.source)} - </span>
												<span className="text-black font-semibold">Arrival: </span>
												<span className="text-black">{toSentenceCase(booking.destination)}</span>
											</div>
											<div>

												<span className="text-black font-semibold">Date: </span>
												<span className="text-black">{booking.date}</span>
											</div>
											<div>
												<span className="text-black font-semibold">Class: </span>
												<span className="text-black">{booking.class}</span>
											</div>
											<div>
												<span className="text-black font-semibold">Available Seats: </span>
												<span className="text-black">{booking.available_seats}</span>
											</div>
											<div>
												<span className="text-black font-semibold">Cost: </span>
												<span className="text-black">₹{booking.cost}</span>
											</div>
											<button className="bg-blue-400 border border-black rounded-full text-gray-900 px-6 py-2 font-semibold hover:bg-gray-700 hover:text-white"
												onClick={() => navigate("/reserve", { state: { booking: { ...booking, count: amount, booking_id: booking.id } } })}
											>
												Book Now
											</button>
										</div>
									);
								})
								:
								<div className="flex flex-row justify-center items-center px-2 py-2 rounded-lg mt-2 flex-1">
									<span className="text-white font-semibold">{filterSearchText}</span>
								</div>
						}
					</div>
					<div>

					</div>
				</div>
				{/* <div className="flex flex-col gap-3 left-animation w-full">
					<span className="text-blue-400 text-[28px] font-medium">
						Welcome To Our Website!
					</span>
					<span className="text-white font-medium md:text-[60px] text-[45px]">
						Luxury Experience <br /> With Our Services.
					</span>
					<span className="text-white font-medium text-[60px]"></span>
					<span className="text-white leading-7 max-w-[500px] text-justify">
						Lorem ipsum dolor sit amet consectetur adipisicing elit. Quisquam nulla ipsa unde
						inventore minus commodi saepe? Eos cumque aliquam consequatur id optio dolorum
						modi quod?
					</span>
					<div className="flex items-center gap-7 mt-5">
						<button className="bg-blue-400 px-6 py-3 text-gray-900 font-semibold rounded-full">
							Book Flight
						</button>
						<button className="border-[2px] border-blue-400 px-6 py-3 text-white font-semibold rounded-full">
							Contact Us
						</button>
					</div>
				</div> */}
				{/* <img
					src={plane}
					className="md:w-[53%] w-full right-animation"
					alt=""
				/> */}
			</div>
		</div>
	);
};

export default BookingHero;
