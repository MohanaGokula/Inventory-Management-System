import React from 'react';
import ReactDOM from 'react-dom';
import login_user from "./img/login.png";
import litvik_logo from "./img/litvik_logo.jpg";
import { useState ,useEffect } from "react";
import axios from "axios";
import './Mirror.css';
import { useCookies } from 'react-cookie';
import {Row,Col,Button} from "reactstrap";
import { AiOutlineHome } from "react-icons/ai";
import { AiOutlineMail} from "react-icons/ai";
import { submitLogin } from './services/LoginServices';
import {displayError} from './helpers';
import Swal from "sweetalert2";

function Login() {
	const [inputs, setInputs] = useState({});
	const [tfa,setTfa] = useState({
		'secret_code':'',
		'qrcode':'',
		'otp':''
	});
	const [error, setError] = useState({});
	const [isSubmitting, setIsSubmitting] = useState(false);
	const [cookies, setCookie] = useCookies(['myToken']);
	const [name, setName] = useCookies(['myName']);
	const [myUserId, setMyUserId] = useCookies(['myUserId']);
	const [category,setCategory] = useCookies(['myCategory']);
	const [superuser,setSuperuser] = useCookies(['mySuperuser']);
	const [position, setPosition] = useState({ latitude: 0, longitude: 0 });
  	
	var options = {
		enableHighAccuracy: true,
		timeout: 5000,
		maximumAge: 0,
	  };
	  
	function success(pos) {
		var crd = pos.coords;
		console.log(`Latitude : ${crd.latitude}`);
		console.log(`Longitude: ${crd.longitude}`);
		console.log(`More or less ${crd.accuracy} meters.`);
		setPosition({
					latitude: crd.latitude,
					longitude: crd.longitude,
				  });
	}
	  
	function errors(err) {
		console.warn(`ERROR(${err.code}): ${err.message}`);
	}

	const handleChange = (event) => {
		const name = event.target.name;
		const value = event.target.value;
		if(name === 'username')
		{
			console.log(name+"name")
			console.log(value+"value")
			if(!value.trim())
			{
				console.log("username data is empty");
				setError(values => ({...values, [name]: "User Name must not be empty"}))
				setIsSubmitting(false); 
			}
			else
			{
				setError(values => ({...values, [name]: ''}))
				setIsSubmitting(true);
			}
			setInputs(values => ({...values, [name]: value}))
		}
		else if(name === 'password')
		{
			console.log(name+"name")
			console.log(value+"value")
			if(!value.trim())
			{
				console.log("psw data is empty");
				setError(values => ({...values, [name]: "Password must not be empty"}))
				setIsSubmitting(false); 
			}
			else
			{
				setError(values => ({...values, [name]: ''}))
				setIsSubmitting(true);
			}
			setInputs(values => ({...values, [name]: value}))
		}
		else if (name === 'otp')
		{
			console.log(name+"name")
			console.log(value+"value")
			if(!value.trim())
			{
				console.log("otp is empty");
				setError(values => ({...values, [name]: "OTP must not be empty"}))
				setIsSubmitting(false); 
			}
			else
			{
				setError(values => ({...values, [name]: ''}))
				setIsSubmitting(true);
			}
			setTfa(values => ({...values, [name]: value}))
		}
	}
	
	useEffect(() => {
		if (navigator.geolocation) {
			navigator.permissions
			  .query({ name: "geolocation" })
			  .then(function (result) {
				console.log(JSON.stringify(result)+"result")
				if (result.state === "granted") {
				  console.log(result.state+"result.state");
				  //If granted then you can directly call your function here
				  navigator.geolocation.getCurrentPosition(success);
				// navigator.geolocation.getCurrentPosition(function (position) {
				// 	setPosition({
				// 	  latitude: position.coords.latitude,
				// 	  longitude: position.coords.longitude,
				// 	});
					// console.log(`latitude : ${position.coords.latitude}`);
					// console.log(`longitude: ${position.coords.longitude}`);
				//   });
				} 
				else if (result.state === "prompt") {
				  navigator.geolocation.getCurrentPosition(success, errors, options);
				} 
				else if (result.state === "denied") {
					// Swal.fire("Pls enable location.", "", "info");
				  console.log("If denied then you have to show instructions to enable location")
				}
				result.onchange = function () {
				  console.log(result.state+"result.state");
				};
			  });
		} 
		else {
			// alert("Sorry Not available!");
			Swal.fire("Sorry Not available!", "", "info");
		}
		console.log(position.latitude+"position.latitude");
		console.log(position.longitude+"position.longitude");
		if(cookies['myToken']){
			console.log(cookies['myToken']+"cookies['myToken']")
			window.location.href = '/Home'
		}
	}, [cookies]);

  	const handleSubmit=(event)=> {
		event.preventDefault();
		console.log(JSON.stringify(error)+"error handleSubmit");
		console.log(isSubmitting+"isSubmitting");
		
		if ((Object.values(error).every(x => !x)) && (isSubmitting))  
		//  && (position.latitude) && (position.longitude)
		{
			submitLogin(inputs.username,inputs.password,tfa.otp,position.latitude,position.longitude)
			.then(function (login_response) {
				// console.log(JSON.stringify(login_response)+"response");
				console.log(JSON.stringify(login_response)+"data");
				if(login_response.tfa_enabled === false)
				{
					console.log(JSON.stringify(login_response.username)+"user");
					console.log(login_response.tfa_enabled+"login_response.tfa_enabled");
					console.log(login_response.otp_base32+"otp_base32");
					console.log(login_response.otp_auth_url+"otp_auth_url");
					setTfa(values => ({...values, ['secret_code']: login_response.otp_base32,['qrcode']:login_response.img_str}))
					setInputs(values => ({...values, ['username']: login_response.username}))
					document.getElementById("tfa").style.display = 'block';
					document.getElementById("login").style.display = 'none';
				}
				else if(login_response.tfa_enabled === true && login_response.state == 'have to verify otp')
				{
					document.getElementById("tfa").style.display = 'block';
					document.getElementById("qr_code").style.display = 'none';
					document.getElementById("login").style.display = 'none';
					console.log(login_response.tfa_enabled && login_response.state+"login_response.tfa_enabled && login_response.state");
				}
				else if (login_response.token) {
					setCookie('myToken',login_response.token);
					setName('myName',login_response.name)
					setMyUserId('myUserId',login_response.user_id)
					
					if(!(login_response.is_superuser)){
						setCategory('myCategory',login_response.category)
						console.log(login_response.category+"login_response.category"+typeof(login_response.category))
					}
					else
					{
						setSuperuser('mySuperuser',login_response.is_superuser)
					}
				} 
				// else{
				// 	setInputs({}) 
				// 	setError({});
				// }
			})
			// .catch((error) => {
			// 	console.log(error.response.data);
			// 	displayError(error.response.data,"Authentication Failed.");
			// });
		}
	}  
    
	return(
        <>
			<h1 style={{color:"rgb(2, 2, 49)",textAlign:"center",paddingTop:"10px"}}>
			<img src={litvik_logo} className="logo"/>  LITVIK SOFTWARE LABS PVT. LTD.</h1>
			
			<div className='container'  id="login">
				<Row>
					<Col xl={4} lg={4} md={4}> 
						<div className="form-row table-bordered shadow p-2 my-2  border-secondary p-2 mb-3 " style={{borderRadius:"10px",fontWeight:"bold",background:"white"}}>
							<h3 style={{color:"rgb(2, 2, 49)",textAlign:"center"}}>Contact Details</h3>
							
							Get in touch with us for any questions about our industries or projects.
							<span style={{paddingTop:"10px"}}>{ <AiOutlineHome size={28}/>}</span>  <h4 style={{color:"rgb(2, 2, 49)",textAlign:"center" ,paddingLeft:"10px",paddingTop:"10px"}}>Office Address</h4>
							<p style={{paddingLeft:"40px"}}>
							Plot No.1, Second Floor, <br/>
							Thiruvalluvar Cross Street, Madambakkam,<br/>
							Chennai, Tamilnadu, India - 600126<br/>
							Mobile No : 95516 14121 <br/>
							{/* {<AiOutlineMail size={28}/>} #0093dd*/}
							sales@litvik.in
							</p>
						</div>
					</Col>
					<Col xl={4} lg={4} md={4}>
						<div className="container loginBox">
							<img src={login_user} className="user" />
							<h3>Login </h3>
								<form className="form" onSubmit={handleSubmit}>
									<label className = "control-label" htmlFor="uname1"><strong>User Name</strong></label>
									<div className="inputBox">
										<span><i className="fa fa-user"></i></span>
										<input type="text" name="username" required onChange={handleChange} value={inputs.username || ""} placeholder="Username"/>
										{error.username && (<><strong className="form-group col-sm-12 text-center text-danger" >{error.username}</strong><br/></>)}
									</div>
									<label className = "control-label" htmlFor="password"><strong>Password</strong></label>
									<div className="inputBox">
										<span><i className="fa fa-lock"></i></span>
										<input type="password" name="password" required onChange={handleChange} value={inputs.password || ""} placeholder="password"/>
										{error.password && (<><strong className="form-group col-sm-12 text-center text-danger" >{error.password}</strong><br/></>)}
									</div>
									<input type="submit" name="" value="Log In"/>
								</form>
						</div>
					</Col>
					<Col xl={4} lg={4} md={4}>
						<div className="form-row table-bordered shadow p-2 my-2  border-secondary p-2 mb-3 " style={{borderRadius:"10px",background:"white"}}>
							<h3 style={{color:"rgb(2, 2, 49)",textAlign:"center"}}>FEATURES</h3>
							Litvik Software Labs Pvt. Ltd. just simplify the Ready Mix Concrete industries operations.

							Litvik ERP used to maintaining daily transctions like 
							<ul>
								<li><span style = {{fontWeight:"bold"}}>Marketing Management</span> (Customer, Project, Sales order)</li>
								<li><span style = {{fontWeight:"bold"}}>Planning Management</span> (Schedule, Prodction, Despatch)</li>
								<li><span style = {{fontWeight:"bold"}}>Accounting Management</span> (Invoice, Receipts, Payments, Banking, Adjustments)</li>
								<li><span style = {{fontWeight:"bold"}}>Fleet Manangement</span> (Maintainging Trucks, Pumps,Drivers, Diesel & Reports)</li>
								<li><span style = {{fontWeight:"bold"}}>Quality Control System</span> (Analysing Materials, Design Mix, Reports)</li>
								<li><span style = {{fontWeight:"bold"}}>Inventory Management</span> (Vendor, Purchase Order, Goods Receipts & Delivery, Stock)</li>
							</ul> 
						</div>	 
					</Col>
				</Row>
			</div>

			<div className="container"  id="tfa" style={{display:"None"}}>
				<Row>
					<Col xl={4} lg={4} md={4}>
					</Col>
					<Col xl={3} lg={3} md={3}>
						<div className="form-row table-bordered shadow p-2 my-2  border-secondary p-2 mb-3 " style={{borderRadius:"10px",fontWeight:"bold",backgroundColor:"white"}}>
							<p id="qr_code" style={{color:"rgb(2, 2, 49)",textAlign:"center"}}>
								<span style={{fontSize:"15px",fontWeight:"bold"}}>Two-Factor Authentication (2FA)</span>
							<br/>
							<span style={{paddingTop:"10px",textAlign:"left",paddingLeft:"4px",color:"blue"}}>Scan QR code</span><br/>
							<img src={`data:image/jpeg;base64,${tfa.qrcode}`} style={{ width:"200px",height:"200px" }}/><br/>
							{/* <span style={{color:"blue",textAlign:"left"}}>or Enter Code into your App .<br/>
							Secret Key :</span> {tfa.secret_code} */}
							</p><br/>
							<form className="form" id="submit_otp"  onSubmit={handleSubmit}>
								<div className="form-group">
									<div className = "input-group">
										<input type="text" className="form-control" name="otp" id="otp" placeholder="Please enter the OTP" onChange={handleChange} value={tfa.otp || ""} required="" />
										{error.otp && (<><strong className="form-group col-sm-12 text-center text-danger" >{error.otp}</strong><br/></>)}
									</div>
								</div>
								<button type="submit" className="btn btn-primary btn-rounded float-left">Verify & Activate</button>
							</form>
						</div>
					</Col>
				</Row>
			</div>
        </>
    );
}
export default Login;