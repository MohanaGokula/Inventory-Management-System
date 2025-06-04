import React from 'react';
import ReactDOM from 'react-dom';
import login_user from "./img/login.png";
import { useState ,useEffect } from "react";
import axios from "axios";
import './Mirror.css';
import { useCookies } from 'react-cookie';
import {Row,Col,Button} from "reactstrap";
import { AiOutlineHome } from "react-icons/ai";
import { AiOutlineMail} from "react-icons/ai";

function Login() {
	const [inputs, setInputs] = useState({});
	const [tfa,setTfa] = useState({
		'secret_code':'',
		'qrcode':'',
		'otp':''
	});
	const [error, setError] = useState({});
	const [isSubmitting, setIsSubmitting] = useState(false);
	const [errors, setErrors] = useState(false);
	const [cookies, setCookie] = useCookies(['myToken']);
	const [name, setName] = useCookies(['myName']);
	const [category,setCategory] = useCookies(['myCategory']);
	const [superuser,setSuperuser] = useCookies(['mySuperuser']);
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
  	// const handleChange2 = (event) =>
   	// {
    // const name2 = event.target.name;
    // const value2 = event.target.value;
	// if(!value2.trim())
    //   {
    //     console.log("username data is empty");
    //     setError(values => ({...values, [name]: "OTP must not be empty"}))
    //     setIsSubmitting(false); 
    //   }
	//   else
	//   {
	// 	setError(values => ({...values, [name]: ''}))
	// 	setIsSubmitting(true);
	//   }
	
	// }
useEffect(() => {
if(cookies['myToken']){
	console.log(cookies['myToken']+"cookies['myToken']")
	window.location.href = '/Home'
}
}, [cookies]);

// const submit_otp=(event)=> {
//     event.preventDefault();
// 	console.log(JSON.stringify(tfa)+"tfa");
// 	console.log(error+"error")
//     console.log(isSubmitting+"isSubmitting")
//     if ((Object.values(error).every(x => !x)) && isSubmitting)  
// 	{
// 		axios.post('http://127.0.0.1:8000/Login/', 
// 		{
// 		otp: (tfa.otp).trim(),
//         }).then(function (response) 
// 		{
// 			console.log(JSON.stringify(response.data)+"data");
// 			if(!response.data.tfa_enabled)
// 			{
// 				console.log(JSON.stringify(response.data.user_name)+"user");
// 				console.log(response.data.tfa_enabled+"response.data.tfa_enabled");
// 				console.log(response.data.otp_base32+"otp_base32");
// 				console.log(response.data.otp_auth_url+"otp_auth_url");
// 				setTfa(values => ({...values, ['secret_code']: response.data.otp_base32,['qrcode']:response.data.img_str}))
// 				document.getElementById("tfa").style.display = 'block';
// 				document.getElementById("login").style.display = 'none';
				
// 			}
// 			else if (response.data.tfa_enabled && response.data.token && response.data.otp_verified) 
// 			{
// 				setCookie('myToken',response.data.token);
// 				setName('myName',response.data.name)
// 				if(!(response.data.is_superuser))
// 				{
// 					setCategory('myCategory',response.data.category)
// 				}
// 				else
// 				{
// 					setSuperuser('mySuperuser',response.data.is_superuser)
// 				}
// 			} 
			
// 			else 
// 			{
// 				setInputs(() => "") 
// 				setErrors(true);
// 			}
//         }).catch(function (error) {
// 		console.log(error+"error");
// 		})
// 	}
// }

const handleSubmit=(event)=> {
    event.preventDefault();
    console.log(error+"error")
    console.log(isSubmitting+"isSubmitting")
    if ((Object.values(error).every(x => !x)) && isSubmitting)  
	{
		axios.post('http://127.0.0.1:8000/login/', 
		{
		username: (inputs.username).trim(),
		password: inputs.password,
		otp : tfa.otp
		}).then(function (response) 
		{
			// console.log(JSON.stringify(response)+"response");
			console.log(JSON.stringify(response.data)+"data");
			if(!response.data.tfa_enabled)
			{
				console.log(JSON.stringify(response.data.username)+"user");
				console.log(response.data.tfa_enabled+"response.data.tfa_enabled");
				console.log(response.data.otp_base32+"otp_base32");
				console.log(response.data.otp_auth_url+"otp_auth_url");
				setTfa(values => ({...values, ['secret_code']: response.data.otp_base32,['qrcode']:response.data.img_str}))
				setInputs(values => ({...values, ['username']: response.data.username,['password']:response.data.password}))
				document.getElementById("tfa").style.display = 'block';
				document.getElementById("login").style.display = 'none';
			}
			else if(response.data.tfa_enabled && response.data.status == 'have to verify otp')
			{
				console.log(response.data.tfa_enabled && response.data.status+"response.data.tfa_enabled && response.data.status");
			}
			else if (response.data.token) 
			{
				setCookie('myToken',response.data.token);
				setName('myName',response.data.name)
				if(!(response.data.is_superuser))
				{
					setCategory('myCategory',response.data.category)
				}
				else
				{
					setSuperuser('mySuperuser',response.data.is_superuser)
				}
			} 
			
			else 
			{
				setInputs(() => "") 
				setErrors(true);
			}
        }).catch(function (error) {
			console.log(error+"error");
		})
    }
}  
    return(
        <>
        <h1 style={{color:"rgb(2, 2, 49)",textAlign:"center",paddingTop:"10px"}}>LITVIK SOFTWARE LABS PVT. LTD.</h1>
		<div className='container' id="login">
			<Row>
				<Col xl={4} lg={4} md={4}> 
					<div className="form-row table-bordered shadow p-2 my-2  border-secondary p-2 mb-3 " style={{borderRadius:"10px",fontWeight:"bold"}}>
					<h3 style={{color:"rgb(2, 2, 49)",textAlign:"center"}}>Contact Details</h3>
					
					Get in touch with us for any questions about our industries or projects.
					<span style={{paddingTop:"10px"}}>{ <AiOutlineHome size={28}/>}</span>  <h4 style={{color:"rgb(2, 2, 49)",textAlign:"center" ,paddingLeft:"10px",paddingTop:"10px"}}>Office Address</h4>
					<p style={{paddingLeft:"40px"}}>Ready Mix ERP <br/>
					174, Time Square Empire,<br/>
					GJ SH 42, Mirjapar,<br/>
					Bhuj, Gujarat<br/>
					370001 - India<br/>
					{/* { <AiOutlineMail size={28}/>} */}
					</p>
					</div>
				</Col>
				<Col  xl={4} lg={4} md={4}>
					<div className="loginBox">
						<div className="glass">
							<img src={login_user} className="user" />
							<h3>Login </h3>
								<form className="form" onSubmit={handleSubmit}>
									{errors === true && <h2 className="form-group col-sm-12  text-center text-danger" >Invalid Credentials</h2>}
									<label className = "control-label" htmlFor="uname1"><strong>User Name</strong></label>
									<div className="inputBox">
										<span><i className="fa fa-user"></i></span>
										<input type="text" name="username" required onChange={handleChange} value={inputs.username || ""} placeholder="Username"/>
										{error.username && (<><strong className="form-group col-sm-12 text-center text-danger" >{error.username}</strong><br/></>)}
									</div>
									<label className = "control-label" htmlFor="password"><strong>Password</strong></label>
									<div className="inputBox">
										<span><i className="fa fa-lock"></i></span>
										<input type="password" name="password" required onChange={handleChange} value={inputs.password || ""}placeholder="password"/>
										{error.password && (<><strong className="form-group col-sm-12 text-center text-danger" >{error.password}</strong><br/></>)}
									</div>
									<input type="submit" name="" value="Log In"/>
								</form>
						</div>
					</div>
				</Col>
			
				<Col xl={4} lg={4} md={4}>
					<div className="form-row table-bordered shadow p-2 my-2  border-secondary p-2 mb-3 " style={{borderRadius:"10px",fontWeight:"bold"}}>
					<h3 style={{color:"rgb(2, 2, 49)",textAlign:"center"}}>FEATURES</h3>
					LiVi Software Solutions just simplify the Ready Mix Concrete industries operations.

					LiVi ERP used to maintaining daily transctions like 
					<ul>
						<li>Marketing Management (Customer, Project, Sales order)</li>
						<li>Planning Management (Schedule, Prodction, Despatch)</li>
						<li>Accounting Management (Invoice, Receipts, Payments, Banking, Adjustments)</li>
						<li>Fleet Manangement (Maintainging Trucks, Pumps,Drivers, Diesel & Reports)</li>
						<li>Quality Control System (Analysing Materials, Design Mix, Reports)</li>
						<li>Inventory Management (Vendor, Purchase Order, Goods Receipts & Delivery, Stock)</li>
					</ul> 
					</div> 
				</Col>
			</Row>
		</div>
		<div className="container"  id="tfa" style={{display:"None"}}>
            <div className="row vertical">
				<div className="col-md-2">
				</div>
				<div  className='col-md-8 center-block'>
					
					<div className="form-row table-bordered shadow p-2 my-2  border-secondary p-2 mb-3 " style={{borderRadius:"10px",fontWeight:"bold",backgroundColor:"white"}}>
						<p>
							<span style={{color:"rgb(2, 2, 49)",textAlign:"center"}}>Two-Factor Authentication (2FA)</span>
						<br/>
						<span style={{paddingTop:"10px",textAlign:"left",paddingLeft:"4px",color:"blue"}}>Scan QR code</span><br/>
						<img src={`data:image/jpeg;base64,${tfa.qrcode}`} style={{ width:"200px",height:"200px" }}/><br/>
						<span style={{color:"blue",textAlign:"left"}}>or Enter Code into your App .<br/>
						Secret Key :</span> {tfa.secret_code}
						</p><br/>
						<form className="form" id="submit_otp"  onSubmit={handleSubmit}>
							<div className="form-group">
								<div className = "input-group">
									<input type="text" className="form-control" name="otp" id="otp" placeholder="please enter the OTP" onChange={handleChange} value={tfa.otp || ""} required="" />
									{error.otp && (<><strong className="form-group col-sm-12 text-center text-danger" >{error.otp}</strong><br/></>)}
								</div>
							</div>
							<button type="submit" className="btn btn-primary btn-rounded float-right">Verify & Activate</button>
						</form>
					</div>
				</div>
			</div>
		</div>
		{/* <div className="container"  id="otp_only" style={{display:"None"}}>
			<div className = "shadow-lg p-3 mb-5 bg-green rounded">
						<div className="card card-outline-secondary">
							<form className="form" id="submit_otp">
								<div className="form-group">
									<div className = "input-group">
										<input type="text" className="form-control" name="otp" id="otp" placeholder="please enter the OTP" required="" />
									</div>
								</div>
								<button type="submit" className="btn btn-primary btn-rounded float-right">Verify & Activate</button>
							</form>
						</div>
					</div>
		</div> */}
	</>
    );
}
export default Login;