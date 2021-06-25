import React from 'react'
import { Route } from 'react-router-dom'
import { BrowserRouter as Router } from 'react-router-dom'
import { Home } from './common/index'



const App = () => {
  return (
    <div>
      <Router>
          <Route exact path='/' component={Home} />
      </Router>
    </div>
  )
}

export default App