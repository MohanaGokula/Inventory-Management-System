import React,{ useState, useEffect, Fragment }  from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter as Router, Redirect, Route,Link,NavLink, Switch } from 'react-router-dom';
import Sidebar from './Sidebar';
import Swal from "sweetalert2";
import { useCookies } from 'react-cookie';

        function Home() {
            const [cookies] = useCookies(['myToken']);
            const [category] = useCookies(['myCategory']);
            const [superuser] = useCookies(['mySuperuser']);
            const [data,setData]=useState([])
            // useEffect(() => {
            //     async function getCharacters() {
            //       const response = await fetch("http://127.0.0.1:8000/SalesOrderWaiting/",{ method: 'GET',
            //       headers: {
            //           'Authorization': `Token ${cookies['myToken']}`,
            //           'Content-Type': 'application/json'
            //       }});
            //       const data = await response.json();
            //     //   console.log(JSON.stringify(data)+"data_SalesOrderWaiting")
            //       if(data.dtl)
            //       {
            //         // console.log(JSON.stringify(data.dtl)+"response_dtl");
            //         setData(data.dtl)
            //       }
            //     }
            //     getCharacters();
            //   }, []);
            //   console.log((data.length)+"data_SalesOrderWaiting")
            return (
            <div className="App" id="outer-container" >
                   <Sidebar pageWrapId={'page-wrap'} outerContainerId={'outer-container'} />
                    <div id="page-wrap">
                        <h1 style={{color:"rgb(2, 2, 49)",textAlign:"center"}}>Welcome to</h1>
                        <h1 style={{color:"rgb(2, 2, 49)",textAlign:"center"}}>Litvik Software Labs Pvt. Ltd.</h1>
                        {(data.length != 0) && ((superuser['mySuperuser']) || (category['myCategory'][0].Is_SO_approval === true)) &&(
                        <div className="container"style={{ backgroundColor: "#d9d9d9",opacity:"0.9"}}>
                        <div className="table-responsive">
                        <table  className="table table-hover table table-striped table-light table table-sm table table-bordered">
                            <thead className="thead-light">
                                <tr><th colSpan="12" style={{backgroundColor:"rgb(56, 108, 187)",color:"white",width:"600px",fontSize:"20px"}} >List of SalesOrder waiting for Approval</th></tr>
                                <tr style={{textAlign:"center"}}>
                                    <th>S.O. NO.</th>
                                    <th>S.O. Date</th>
                                    <th>Plant location</th>
                                    <th>Customer</th>
                                    <th>Site</th>
                                    <th>Grade</th>
                                    <th>Rate</th>
                                    <th>Order Qty.</th>
                                    <th>Balance qty</th>
                                    <th>Delivery Mode</th>
                                    <th>Approval status</th>
                                    <th style={{width: "11%"}}>Action</th>
                                </tr>
                            </thead>
                        <tbody>
                            {data.map((dtl) => (
                            <tr key={dtl.id} >
                                <td>{dtl.soDSlNo}</td>
                                <td>{dtl.soDSlDt}</td>
                                <td>{dtl.cmpAlias}</td>
                                <td>{dtl.CusName}</td>
                                <td>{dtl.cusProjectName}</td>
                                <td>{dtl.prodName}</td>
                                <td>{dtl.soDRate}</td>
                                <td>{dtl.soDOrdQty}</td>
                                <td>{dtl.soDBalQty}</td>
                                <td>{dtl.soDDeliveryMode}</td>
                                <td>{dtl.soDapprstatus}</td>
                                <td> 
                                        <Link to={`/SOApproval/${dtl.id}/`} className="btn btn-primary btn-sm">
                                        To Approve    
                                        </Link>
                                </td>
                            </tr>
                            ))}
                        </tbody>
                    </table>
                    </div>
                    </div>
                        )}
                    </div>
            </div>
        );
    };
  
  export default Home;