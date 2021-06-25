import React, {useEffect} from 'react'
import axios from 'axios'

const Home = () => {
    useEffect(()=>{
      axios({
        method: "get",
        url: "http://127.0.0.1:8000/hello",
        responseType: "json"
    }).then(function (response) {
        alert(response.data.greeting)
    })
    },[])


    return (
        <>
          <h1>홈</h1>
          <A />
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
    <button>
      {props.value}
    </button>
  )
}

