import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

type ErrorObject = {
	error: string;
	shouldRedirect: boolean;
	shouldPersist: boolean;
}

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

const validate = (email: string, password: string, repeatPassword: string): boolean => {
	if (email === '' || password === '' || repeatPassword === '')
		return false;

	return true;
}



const ReservationHero = () => {
	const [error, setError] = useState<ErrorObject | null>(null);
	const [timeRemaining, setTimeRemaining] = useState<number>(10);

	const [info, setInfo] = useState<string[] | null>(null);

	const [email, setEmail] = useState<string>('');
	const [password, setPassword] = useState<string>('');
	const [repeatPassword, setRepeatPassword] = useState<string>('');

	const [showDeleteButton, setShowDeleteButton] = useState<boolean>(false);

	const [booking_id, setBookingId] = useState<string>('');
	const [payment_id, setPaymentId] = useState<string>('');

	const location = useLocation();
	const navigate = useNavigate();

	const { state } = location;
	const data = state || null;

	useEffect(() => {
		if (data == null || data.booking == null || data.booking.booking_id == null || data.booking.count == null) {
			setError({ error: 'Something went Wrong, Please try again', shouldRedirect: true, shouldPersist: true });
		} else {
		} else {
			console.log(data.booking);
		}
	}, []);

	useEffect(() => {
		if (error && error.shouldRedirect) {
			const countdown = async () => {
				for (let i = timeRemaining; i >= 0; i--) {
					setTimeRemaining(i); // Update the state with the current count
					await sleep(1000); // Sleep for 1 second (1000 milliseconds)
				}
			};
			countdown();
		}
	}, [error]);

	useEffect(() => {
		if (timeRemaining === 0) {
			navigate('/booking');
		}
	}, [timeRemaining]);

	const signUp = async () => {
		let info_temp = ['> Validating Credentials for Sign Up...'];
	const signUp = async () => {
		let info_temp = ['> Validating Credentials for Sign Up...'];
		if (!validate(email, password, repeatPassword)) {
			setError({ error: 'Please fill in all the fields correctly', shouldRedirect: false, shouldPersist: false });
			return;
		}

		if (password !== repeatPassword) {
			setError({ error: 'Passwords do not match', shouldRedirect: false, shouldPersist: false });
			setError({ error: 'Please fill in all the fields correctly', shouldRedirect: false, shouldPersist: false });
			return;
		}

		if (password !== repeatPassword) {
			setError({ error: 'Passwords do not match', shouldRedirect: false, shouldPersist: false });
			return;
		}

		setInfo([...info_temp]);

		try {
			const signUpResponse = await fetch('http://localhost:9000/route/authentication/signup', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					username: email,
					password: password,
				})
			});

			if (signUpResponse.status !== 200) {
				info_temp.push('> Sign Up Failed... Try again');
				setInfo([...info_temp]);
				const errorData = await signUpResponse.json();
				throw new Error(errorData.message || 'Sign Up Failed');
			}

			info_temp.push('> Sign Up Successful... You can now log in');
			setInfo([...info_temp]);

			await signUpResponse.json();
		} catch (error: any) {
			console.error(error);
			setError({ error: `Unable to Sign Up: ${error.message}`, shouldRedirect: false, shouldPersist: false });
			throw error;
		}
	};

	const login = async () => {
		let info_temp = ['> Checking your credentials in our database...'];
	const login = async () => {
		let info_temp = ['> Checking your credentials in our database...'];
		if (!validate(email, password, repeatPassword)) {
			setError({ error: 'Please fill in all the fields', shouldRedirect: false, shouldPersist: false });
			return;
		}


		setInfo([...info_temp]);


		try {
			const loginResponse = await fetch('http://localhost:9000/route/authentication/login', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					username: email,
					password: password
				})
			});
			});

			if (loginResponse.status !== 200) {
				info_temp.push('> Invalid Credentials... Try again');
				setInfo([...info_temp]);
				const errorData = await loginResponse.json();
				throw new Error(errorData.message || 'Invalid Credentials');
				info_temp.push('> Invalid Credentials... Try again');
				setInfo([...info_temp]);
				const errorData = await loginResponse.json();
				throw new Error(errorData.message || 'Invalid Credentials');
			}

			info_temp.push('> Login Successful');
			setInfo([...info_temp]);
			info_temp.push('> Login Successful');
			setInfo([...info_temp]);

			await loginResponse.json();

			// Redirect or proceed with other actions upon successful login
		} catch (error: any) {
			console.error(error);
			setError({ error: `Unable to Login: ${error.message}`, shouldRedirect: false, shouldPersist: false });
			throw error;
		}
	};



	const createAccountAndBook = async () => {
		let info_temp = ['> Credentials format Valid... Logging in'];

		if (!validate(email, password, repeatPassword)) {
			setError({ error: 'Please fill in all the fields', shouldRedirect: false, shouldPersist: false });
			return;
		}
		setInfo([...info_temp]);

		try {
			await signUp();

			// Proceed with booking after successful sign-up
			const reservationResponse = await fetch('http://localhost:9000/route/reservation/makereservation', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					email: email,
					booking_id: data.booking.booking_id,
					count: data.booking.count,
				}),
			});

			if (reservationResponse.status !== 200) {
				info_temp.push('> Unable to make reservation... Exiting');
				throw new Error('Reservation Failed');
			}
			info_temp.push('> Reservation Successful... Making Payment');
			setInfo([...info_temp]);

			const reservationResult = await reservationResponse.json();
			setBookingId(reservationResult.id);

			// Proceed with payment or further actions after successful reservation
			const paymentResponse = await fetch('http://localhost:9000/route/payment/makepayment', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					email: email,
					booking_id: data.booking.booking_id,
					cost: data.booking.count,
				}),
			});

			if (paymentResponse.status !== 200) {
				info_temp.push('> Unable to make payment... Exiting');
				throw new Error('Payment Failed');
			}

			const paymentResult = await paymentResponse.json();
			setPaymentId(paymentResult.id);

			info_temp.push('> Payment Successful... Please Check Inbox for Confirmation');
			setInfo([...info_temp]);

			setShowDeleteButton(true);

		} catch (err: any) {
			console.error(err);
			setError({ error: `An error has occurred. ${err.message}`, shouldRedirect: false, shouldPersist: false });
		}
	};

	const signInAndBook = async () => {
		let info_temp = ['> Credentials format Valid... Logging in'];

		if (!validate(email, password, repeatPassword)) {
			setError({ error: 'Please fill in all the fields', shouldRedirect: false, shouldPersist: false });
			return;
		}

		setInfo([...info_temp]);

		try {
			await login();

			// Attempt to make reservation
			const reservationResponse = await fetch('http://localhost:9000/route/reservation/makereservation', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					email: email,
					booking_id: data.booking.booking_id,
					count: data.booking.count,
				}),
			});

			if (reservationResponse.status !== 200) {
				info_temp.push('> Unable to make reservation... Exiting');
				throw new Error('Reservation Failed');
			}

			info_temp.push('> Reservation Successful... Making Payment');
			await reservationResponse.json();

			setInfo([...info_temp]); // Ensure state updates by spreading info_temp

			// Payment logic here; Attempt to make reservation
			const paymentResponse = await fetch('http://localhost:9000/route/payment/makepayment', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					email: email,
					booking_id: data.booking.booking_id,
					cost: data.booking.count,
				}),
			});

			if (paymentResponse.status !== 200) {
				info_temp.push('> Unable to make payment... Exiting');
				throw new Error('Payment Failed');
			}

			info_temp.push('> Payment Successful... Please Check Inbox for Confirmation');
			setInfo([...info_temp]);
			setInfo([...info_temp]);
			// You can proceed to payment or further actions here based on reservationData

		} catch (error: any) {
			console.error(error);

			if (error.message === 'Invalid Credentials') {
				setError({ error: `Unable to Login: ${error}`, shouldRedirect: false, shouldPersist: false });
			} else {
				setError({ error: `Unable to make reservation: ${error}`, shouldRedirect: false, shouldPersist: false });
			}
		}

	};

	async function cancel() {
		fetch('http://localhost:9000/route/reservation/cancelreservation', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				booking_id: booking_id,
				payment_id: payment_id,
				count: data.booking.count
			}),
		}).then(_ => {
			navigate('/booking');
		});

	}


	console.log("update");

	return (
		<div className="hero z-[1] w-full h-[100vh] grid place-items-center bg-[#141b2b] relative">
			<div className="flex md:flex-row flex-col items-center w-full md:px-[200px] px-8 justify-between md:gap-0 gap-28">

				<div className="container mx-auto border border-blue-400 flex-1 flex flex-col rounded-lg md:px-[50px] px-8 md:py-[25px]">

					{
						info && info.length != 0 && (
							// SHow a dialog box with the error message
							<div
								className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50"
							>
								<div
									className="bg-white rounded-lg shadow-lg max-w-sm mx-auto p-10"
									onClick={(e) => e.stopPropagation()}
								>
									<h2 className="text-xl font-semibold text-green-600">Notification</h2>
									<ol className="mt-2 text-gray-700">
										{
											info.map((msg, index) => {
												return (
													<li key={index + msg}>{msg}</li>
												)
											})
										}

									</ol>
									{showDeleteButton && (<button className="bg-red-400 rounded-full text-gray-900 px-6 py-2 font-semibold hover:bg-gray-700 hover:text-white"
										onClick={() => {

											// make api call to delete booking and payment
											// setError("booking cancelled")
											// navigate to booking
											const info_temp = info;
											info_temp.push('> Cancelling Reservation... You will be redirected once this completed');
											setInfo([...info_temp]);
											cancel();
										}}
									>Cancel Reservation?
									</button>)}
									{showDeleteButton || error?.error != "" ? null :
										<button className="bg-green-400 rounded-full text-gray-900 px-6 py-2 font-semibold hover:bg-gray-700 hover:text-white"
											onClick={() => { setInfo(null) }}>Close</button>
									}
								</div>
							</div>
						)
					}

					{
						error && error.error != "" && (
							// SHow a dialog box with the error message
							<div
								className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50"
								onClick={() => { if (error.shouldPersist) return; setError({ ...error, error: '' }) }}
							>
								<div
									className="bg-white rounded-lg shadow-lg max-w-sm mx-auto p-6"
									onClick={(e) => e.stopPropagation()}
								>
									<h2 className="text-xl font-semibold text-red-600">Error</h2>
									<p className="mt-2 text-gray-700">
										{
											error.shouldRedirect ? <>
												An error has occurred. Please try again later. You will be automatically Redirected Back in <span className="text-red-500 font-bold"> {timeRemaining} </span>seconds
											</> : error.error
										}

									</p>
								</div>
							</div>
						)
					}

					{
						<div className="h-[60vh] flex flex-col">
							<h1 className="text-3xl text-white font-semibold">Reservation Details</h1>
							<div className="mb-4">
								<label
									htmlFor="input-field"
									className="block text-gray-700 font-bold mb-2 text-white"
								>
									Email
								</label>
								<input
									id="email"
									type="text"
									value={email}
									onChange={(e) => setEmail(e.target.value)}
									placeholder="Example: john.Doe@example.com"
									className="border border-gray-300 rounded-lg p-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
								/>
							</div>

							<div className="mb-4">
								<label
									htmlFor="input-field"
									className="block text-gray-700 font-bold mb-2 text-white"
								>
									Password
								</label>
								<input
									id="password"
									type="password"
									value={password}
									onChange={(e) => setPassword(e.target.value)}
									placeholder="Min 8 Characters"
									className="border border-gray-300 rounded-lg p-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
								/>
							</div>

							<div className="mb-4">
								<label
									htmlFor="input-field"
									className="block text-gray-700 font-bold mb-2 text-white"
								>
									Repeat Password
								</label>
								<input
									id="repeat-password"
									type="password"
									value={repeatPassword}
									onChange={(e) => setRepeatPassword(e.target.value)}
									placeholder="Should be Same as above"
									className="border border-gray-300 rounded-lg p-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
								/>
							</div>

							<div>
								<button
									className="bg-blue-400 rounded-full text-gray-900 px-6 py-2 font-semibold hover:bg-gray-700 hover:text-white"
									onClick={signInAndBook}
								>Sign in and Book</button>

								<button
									className="bg-blue-400 rounded-full text-gray-900 mx-6 px-6 py-2 font-semibold hover:bg-gray-700 hover:text-white"
									onClick={createAccountAndBook}
								>Create Account and Book</button>

							</div>

						</div>
					}

				</div>
			</div>
		</div>
	);
};

export default ReservationHero;