import React,{useState} from 'react';
import './PasswordStrengthMeter.css';
import {
  Row,
  Col,
  Button,
} from "reactstrap";
const PasswordStrengthMeter = (props) => {
  const testedResult = props.password;
  // const [testedResult, settestedResult] = useState('')
  // React.useEffect(() => {
  //   settestedResult(props.password)
  // }, [props.password,props.actions]);
  const createPasswordLabel = () => {
    let score = 0
    let regexPositive = ["[A-Z]","[a-z]","[0-9]","\\W",]
    regexPositive.forEach((regex, index) => {
      if (new RegExp(regex).test(testedResult)) {
        score +=1
      }
    })
    switch (score) {
      case 0:
        return ({
          value: 0,
          info: "",
        });
      case 1:
        return ({
          value: 1,
          info: "Weak",
        });
      case 2:
        return ({
          value: 2,
          info: "Fair",
        });
      case 3:
        return ({
          value: 3,
          info: "Good",
        });
      case 4:
        return ({
          value: 4,
          info: "Strong",
        });
      default:
        return null
    }
  }
  // {props.actions(createPasswordLabel().info)}

  return (
  <>
  {props.password && ( 
    <div className="container">
        <br/>
        <Row>
          <Col xl={4} lg={4} md={4} sm={4}>
          </Col>
          <Col xl={7} lg={7} md={7} sm={7}>
            <progress className={`password-strength-meter-progress strength-${createPasswordLabel().info} float-right `} value={createPasswordLabel().value} max="4" />
            <br />
            <p className={`password__label strength-${createPasswordLabel().info} float-left`}>Password strength :&nbsp;&nbsp; <span className="float-right">{createPasswordLabel().info} </span></p> 
          </Col>
        </Row>
    </div>
  )}
  </>
   )
  }
export default PasswordStrengthMeter;
