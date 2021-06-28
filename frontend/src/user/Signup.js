import Rect, { useState } from 'react'

const SignUp = () => {
    const [userInfo, setUserInfo] = useState({
        username: '',
        password: '',
        name: '',
        email: '',
    })

    const {username, password, name, email} = userInfo

    const handleChange = e => {
        e.preventDefault()
        const {name, value} = e.target
        alert
    }

    const handlecSumit = e => {
        e.preventDefault()
    }

    return(
      <>
        <form action='/action_page.php' style={{border:'1px solid #ccc'}}>
          <div className='container'>
            <h1>Sign up</h1>
            <p>Please fill out the empty boxes below to sign up</p>
          </div>    
        </form>  
      </>
    )
}

export default SignUp