import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';
import React from 'react';
import { useState, useEffect } from 'react';
import {  useParams } from 'react-router-dom';
import { useCookies } from 'react-cookie';

function DisplayPDF({exportPDF, parentCallBack, record}){
    const printRef = React.useRef();
    console.log(record+"record_dis")
    const [inputs, setInputs] = useState({});
    const [cookies] = useCookies(['myToken']);
    useEffect(() => {
        if(exportPDF){
            const printPDF = async () => {
                const res = await fetch(`http://127.0.0.1:8000/SalesOrder/${record}/`,{ method: 'GET',
          headers: {
              'Authorization': `Token ${cookies['myToken']}`,
              'Content-Type': 'application/json'
          }});
          const a = await res.json();
          
            console.log(JSON.stringify(a)+"SalesOrderPrint");
            setInputs(a.hdr[0])
                const element = printRef.current;
                const canvas = await html2canvas(element);
                const data = canvas.toDataURL('image/png');
            
                const pdf = new jsPDF();
                const imgProperties = pdf.getImageProperties(data);
                const pdfWidth = pdf.internal.pageSize.getWidth();
                const pdfHeight =
                  (imgProperties.height * pdfWidth) / imgProperties.width;
            
                pdf.addImage(data, 'PNG', 0, 0, pdfWidth, pdfHeight);
         pdf.save("download.pdf");
           parentCallBack(false)
         }
            printPDF()
         }},[exportPDF])

    const companynameStyle = {
        fontSize: "25px",
        height: "40px",
        textAlign: "center",
        color: "#000080",
        fontWeight: "bold"
    };

    const addressStyle = {
        fontSize: "15px",
        height: "40px",
        textAlign: "center",
        color: "#964B00"
    };

    const purchaseOrderStyle = {
        fontSize: "20px",
        height: "40px",
        textAlign: "center",
        color: "rgb(100,10,96)"
    };

    const gstNoStyle = {
        fontSize: "20px",
        height: "40px",
        textAlign: "center"
    }
    const billingAddressStyle = {
        backgroundColor:"#dadaf7",
        padding:"5px",
        marginTop:"5px"
    }
    
    const billCusNameStyle = {
        paddingTop:"2px",
        paddingBottom:"2px",
        margin:"2px"
    }
    const billCusAdd1Style = {
        paddingTop:"2px",
        paddingBottom:"2px",
        margin:"2px"  
    }
    const billCusAdd2Style ={
        paddingTop:"2px",
        paddingBottom:"2px",
        margin:"2px"  
    }
    const billCusAdd3Style ={
        paddingTop:"2px",
        paddingBottom:"2px",
        margin:"2px"  
    }
    const billCusPinCodeStyle ={
        paddingTop:"2px",
        paddingBottom:"2px",
        margin:"2px"  
    }
    const billCusMobileNoStyle ={
        paddingTop:"2px",
        paddingBottom:"2px",
        margin:"2px"  
    }
    const billCusTinNoStyle ={
        paddingTop:"2px",
        paddingBottom:"2px",
        margin:"2px"  
    }
    const siteAddressStyle ={
        backgroundColor:"#dadaf7",
        padding:"5px",
        marginTop:"5px"
    }
    const siteCusNameStyle ={
        paddingTop:"2px",
        paddingBottom:"2px",
        margin:"2px"

    }
    const siteCusAdd1Style ={
        paddingTop:"2px",
        paddingBottom:"2px",
        margin:"2px"
    }
    const siteCusAdd2Style ={
        paddingTop:"2px",
        paddingBottom:"2px",
        margin:"2px"

    }
    const siteCusAdd3Style ={
        paddingTop:"2px",
        paddingBottom:"2px",
        margin:"2px"

    }
    const siteCusPinCodeStyle ={
        paddingTop:"2px",
        paddingBottom:"2px",
        margin:"2px"

    }
    const siteCusMobileNoStyle ={
        paddingTop:"2px",
        paddingBottom:"2px",
        margin:"2px"

    }
    const postOfficeStyle ={
        lineHeight:"40px",
        paddingTop:"2px",
        paddingBottom:"2px",
        margin:"2px",
        verticalAlign:"middle"

    }
    const dateStyle ={
        lineHeight:"40px",
        paddingTop:"2px",
        paddingBottom:"2px",
        margin:"2px",
        verticalAlign:"middle"
    }
    const dateOfDeliveryStyle ={
        lineHeight:"40px",
        paddingTop:"2px",
        paddingBottom:"2px",
        margin:"2px",
        verticalAlign:"middle"
    }
    const timeOfDeliveryStyle ={
        lineHeight:"40px",
        paddingTop:"2px",
        paddingBottom:"2px",
        margin:"2px",
        verticalAlign:"middle"
    }
    const saleRepStyle ={
        lineHeight:"40px",
        paddingTop:"2px",
        paddingBottom:"2px",
        margin:"2px",
        verticalAlign:"middle"
    }
    const modeoOfDeliveryStyle={
        lineHeight:"40px",
        paddingTop:"2px",
        paddingBottom:"2px",
        margin:"2px",
        verticalAlign:"middle"
    }
    const distanceFromPlantStyle={
        lineHeight:"30px",
        paddingTop:"2px",
        paddingBottom:"2px",
        margin:"2px"

    }
    const landMarkStyle={
        lineHeight:"30px",
        paddingTop:"2px",
        paddingBottom:"2px",
        margin:"2px"

    }
    const contactPersonStyle={
        lineHeight:"30px",
        paddingTop:"2px",
        paddingBottom:"2px",
        margin:"2px"

    }
    const modeOfPaymentStyle={
        paddingTop:"2px",
        paddingBottom:"2px",
        margin:"2px"
    }
    const amountStyle={
        paddingTop:"2px",
        paddingBottom:"2px",
        margin:"2px"
    }
    const chequeNoStyle={
        paddingTop:"2px",
        paddingBottom:"2px",
        margin:"2px"
    }
    const chequeDateStyle={
        paddingTop:"2px",
        paddingBottom:"2px",
        margin:"2px"

    }
    const bankNameStyle={
        paddingTop:"2px",
        paddingBottom:"2px",
        margin:"2px"

    } 
    const branchStyle={
        paddingTop:"2px",
        paddingBottom:"2px",
        margin:"2px"

    }
    return(
        
<div  ref={printRef} id="divToPrint">
            <div style={{texAlign:"center",fontSize:"20px"}}>
	
                <table border={"2"} width={"100%"}>
                    <tbody>
                <tr>
                <td width={"100px"}>{"{{maincompany.MCCompLogo}}"}</td>
                <td>
                    
                    <div>
                    <div style={companynameStyle}>{"{{hdr.SoHMCompCode.MCName}}"}</div>
                    <div style={addressStyle}>
                    
                    {"{{hdr.SoHMCompCode.MCAdd1}}"}, {"{{hdr.SoHMCompCode.MCAdd2}}"}, {"{{hdr.SoHMCompCode.MCAdd3}}"},
                    <br/>
                    {"{{hdr.SoHMCompCode.MCPhoneno}}"},{"{{hdr.SoHMCompCode.MCMobileno}}"} ,&nbsp;{"{{hdr.SoHMCompCode.MCEmailid}}"}
                    </div>
                    <div style={purchaseOrderStyle}>PURCHASE ORDER</div>
                    <div style={gstNoStyle}>GST No:{"{ {hdr.SoHMCompCode.MCGstno}}"}</div>
                    </div>
                </td>
                </tr>
                </tbody> </table>
                
            </div>
            <div style={{textAlign:"center",fontSize:"20px"}}>
            <div style={{borderStyle:"double",borderWidth:"4px",width:"600px"}} >
                <table><tbody>
                <tr>
                <td width={"45%"}>
                <div style={ billingAddressStyle}><b>{inputs.soHSlNo || ""}BILLING ADDRESS</b></div>
                <div style={{fontSize:"11px",height:"150px",textAlign:"left",padding:"10px"}}>
                    <div style={billCusNameStyle}>{"{{so.soDCusSCode.cusName}}"}</div>
                    <div style={billCusAdd1Style}>{"{{so.soDCusSCode.cusAdd1}}"}</div>
                    <div style={billCusAdd2Style}>{"{{so.soDCusSCode.cusAdd2}}"}</div>
                    <div style={billCusAdd3Style}>{"{{so.soDCusSCode.cusAdd3}}"}</div>
                    <div style={billCusPinCodeStyle}>{"{{so.soDCusSCode.cusPincode}}"}</div>
                    <div style={billCusMobileNoStyle}>{"{{so.soDCusSCode.cusMobileNo}}"}</div>
                    <div style={billCusTinNoStyle}>TIN NO:&nbsp;&nbsp; {"{{so.soDCusSCode.cusMobileNo}}"}</div>
	            </div>
                <div style={siteAddressStyle}><b>SITE ADDRESS</b></div>
	            <div style={{fontSize:"11px",height:"150px",textAlign:"left", padding:"10px"}}>
                    <div style={siteCusNameStyle}>{"{{so.soDCusSCode.cusName}}"}</div>
                    <div style={siteCusAdd1Style}>{"{{so.soDCusSCode.cusAdd1}}"}</div>
                    <div style={siteCusAdd2Style}>{"{{so.soDCusSCode.cusAdd2}}"}</div>
                    <div style={siteCusAdd3Style}>{"{{so.soDCusSCode.cusAdd3}}"}</div>
                    <div style={siteCusPinCodeStyle}>{"{{so.soDCusSCode.cusPincode}}"}</div>
                    <div style={siteCusMobileNoStyle}>{"{{so.soDCusSCode.cusMobileNo}}"}</div>
	            </div>	
                </td>
                <td style={{verticalAlign:"top"}}>
                <div style={{fontSize:"11px",height:"300px",textAlign:"left",padding:"10px"}}>
                    <div style={postOfficeStyle }>PO.No &nbsp;	&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;{"{{hdr.soHPoNo}}"}</div>
                    <div style={ dateStyle}>Date	&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {"{{hdr.soHPoDt}}"}</div>
                    <div style={dateOfDeliveryStyle}> Date of Delivery&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{"{{hdr.soHDeliveryDt}}"}</div>
                    <div style={ timeOfDeliveryStyle}>Time of Delivery&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;	 </div>
                    <div style={saleRepStyle}>SalesRep&nbsp;&nbsp;&nbsp;{"{{hdr.soHCusBCode.cusSalescode.SrName}}"}</div>
                    <div style={ modeoOfDeliveryStyle}>Mode.of.Delivary	Manual/Pump&nbsp;&nbsp;&nbsp;&nbsp;{"{{hdr.soDDeliveryMode}}"}</div>
                </div>
                </td>
                </tr>
                </tbody> </table>
	             </div>
            </div>		
            <div style={{textAlign:"center",fontSize:"20px"}}>
	        <table border={"1"} width={"55%"}>
                <tbody>

                <tr>
                <td width={"25%"}>
                <div style={{fontSize:"12px",height:"150px",textAlign:"left", padding:"10px"}}>
                    <div style={distanceFromPlantStyle}>Distance from Plant(1 way): &nbsp;&nbsp;&nbsp; {"{{hdr.soDCusSCode.cusRadiusDistance}}"}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp; Nature of Work</div>
                    <div style={landMarkStyle}>Land Mark : &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {"{{hdr.soDCusSCode.cusRadiusDistance}}"}&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Pipeline (Reqd)</div>	 	
                    <div style={contactPersonStyle}>Contact Person:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {"{{hdr.soHSiteContactPerson}}"}&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Mobile No:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{"{{hdr.soHSiteContactMobileNo}}"}	</div>
                </div>		
                </td>
                </tr>
                </tbody> </table>
            </div>
            <div style={{textAlign:"center",fontSize:"20px",borderTop:"5px"}}>{"{{% for item in items %} {% endfor %}}"}</div>
                <div style={{borderStyle:"double",borderWidth:"2px",width:"700px"}} >
                <table border={"0"}>
                    <tbody>
                <tr style={{fontSize:"12px"}}>
                    <td  align="center">Sl.No</td>
                    <td align="center">Grade & Particulars</td>
                    <td align="center">Qty</td>
                    <td align="center">Rate</td>
                    <td align="center">Amount</td>
                </tr>
                <tr style={{fontSize:"12px"}}>
                    <td>{"{{item.soDSlNo}}__{{item.soDSqlNo}}"}</td>
                    <td>{"{{item.soDProdCode.prodName}}"}</td>
                    <td>{"{{item.soDOrdQty}}"}</td>
                    <td>{"{{item.soDRate}}"}</td>
                    <td>{"{{item.soDRate}}"}</td>
	            </tr>	
                <tr style={{fontSize:"12px"}}>
                    <td colSpan="4" align="right">Gross Amt</td>
                    <td>&nbsp;</td>
                    </tr>
                    <tr style={{fontSize:"12px"}}>
                    <td colSpan="4" align="right">Add:</td>
                    <td>&nbsp;</td>
                </tr>
                </tbody></table>
                </div> 
            <div style={{textAlign:"center",fontSize:"20px"}}>		
                <table border={"2"}>
                    <tbody>
                    <tr>	
                    <td>	
                        
                 <div style={{fontSize:"11px",paddingLeft:"5px",textAlign:"left"}}>
                    <div>We agree the following terms & conditions.
                        </div>
                        <div>
                            <ul style={{padding:0,marginLeft:"15px",marginTop:"2px",textAlign:"left"}}>
                            <li>The above price is inclusive of all taxes and duties.</li>
                            <li>Supply of ready mix concrete does not include any labour and hence TDS u/s 194C of income tax act is not applicable.</li>
                            <li>The ordered quantity is less than 24 cum per pouring, mobilization expenses shall be borne by us / me as per order.</li>
                            <li>The concrete is ordered and dispatched from your plant, the value of such consignment shall be borne by us / me.</li>
                            <li>Advance payment in the form of Cheque / DD in favour of "VELAVAN CONCRETE" Payable at Chennai.</li>
                            </ul>
                        </div>
                            I / We agree to the above terms & conditions mentioned in the above refeered offer / purchase order.<br /><br />
                            Name :<br />
                            Date :<br />
                            Customer's/Representative's signature with seal.
                    </div>    
                    </td>
                    </tr>		
                    </tbody> </table>
            </div>
                <div>
                <table border="1">   <tbody>
                <tr>
                <td style={{textAlign:"center",paddingTop:"2px"}}>
                    <div style={{padding:"5px",marginTop:"5px"}}><b>ADVANCE PAYMENT</b></div>
                    <div style={{fontSize:"10px",textAlign:"left", padding:"5px"}}>
                        <div style={modeOfPaymentStyle}>Mode of Payment:{"{{hdr.sohAdvMode}}"}</div>
                        <div style={amountStyle}>Amount : {"{{hdr.soHAdvAmt}}"}</div>
                        <div style={chequeNoStyle}> Cheque/DD No : {"{{hdr.sohAdvMode}}"}</div>
                        <div style={chequeDateStyle}>Cheque/DD Date :{"{{hdr.soHAdvInsDt}}"} </div>
                        <div style={bankNameStyle}>Bank Name: {"{{hdr.soHAdvBank}}"}</div>
                        <div style={branchStyle}>Branch : {"{{hdr.soHAdvBranch}}"}</div>
                      </div>  
                    </td>
                    </tr>
                    </tbody> </table>
                </div>
                
 </div>
         
    );
} 


export default DisplayPDF;