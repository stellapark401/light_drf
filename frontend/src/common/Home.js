import React, {useEffect, useState } from 'react'
import axios from 'axios'
import { Button } from '@material-ui/core'


const Home = () => {
    /*useEffect(()=>{
    },[
      axios({
        method: "get",
        url: "http://127.0.0.1:8000/hello",
        responseType: "json"
      }).then(function (response) {
          alert(response.data.message)
      })
    ])

    useEffect(()=>{
    },[
      axios({
        method: "get",
        url: "http://127.0.0.1:8000/",
        responseType: "json"
      }).then(function (response) {
          alert(response.data.greeting)
      })
    ])*/
   
    const handleClick = (e) => {
      e.preventDefault()
      axios({
        method: "get",
        url: "http://127.0.0.1:8000/connection",
        responseType: "json"
      }).then(function (res) {
          setConnection(res.data.connection === 'successful')
          setMsg('button has pushed')
      })
      
    }

    const [connection, setConnection] = useState(false)

    const [msg, setMsg] = useState("button hasn't pushed")

    return (
        <>
          <h1>홈</h1>
          <A />
          <Button onClick={handleClick} >Testing the connection</Button>
          <tr><td>{msg}</td></tr>
          <tr><td>{connection ? 'using: localStorage, connection has set': 'using: localStorage, connection not set'}</td></tr>
        </>
    )
}

export default Home

class A extends React.Component{
  constructor(props){
    super(props)
    this.state = {
      value: '던진다.'
    }
  }
  render () {
    return (
      <B value={this.state.value} />
    )
  }
}

function B(props){
  return(
    <Button>
      {props.value}
    </Button>
  )
}

