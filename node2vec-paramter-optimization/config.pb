language: PYTHON
name: "test-runner"

variable {
 name: "PQRatio"
 type: ENUM
 size: 1
 options: "0.5"                                                                                                                  
 options: "1.0"                                                                                                                  
 options: "2.0"                                                                                                                  
 options: "0.25"                                                                                                                 
 options: "4.0"                                                                                                                  
 options: "0.125"                                                                                                                
 options: "0.0625"                                                                                                               
 options: "4000.0"                                                                                                               
 options: "8.0"                                                                                                                  
 options: "1000.0"                                                                                                               
 options: "0.0005"                                                                                                               
 options: "16.0"                                                                                                                 
 options: "2000.0"                                                                                                               
 options: "500.0"                                                                                                                
 options: "0.004"                                                                                                                
 options: "250.0"                                                                                                                
 options: "0.002"                                                                                                                
 options: "0.001"                                                                                                                
 options: "0.00025"
}

variable {
 name: "d"
 type: ENUM
 size: 1
 options: "64"
 options: "128"
}

variable {
 name: "r"
 type: ENUM
 size: 1
 options: "1"
 options: "3"
}

variable {
 name: "k"
 type: ENUM
 size: 1
 options: "5"
 options: "10"
}

variable {
 name: "l"
 type: ENUM
 size: 1
 options: "40"
 options: "80"
}