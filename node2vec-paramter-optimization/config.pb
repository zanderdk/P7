language: PYTHON
name: "test-runner"

variable {
 name: "p"
 type: ENUM
 size: 1
 options: "0.5"                                                                                                                  
 options: "1.0"                                                                                                                  
 options: "2.0"                                                                                                                  
 options: "0.25"                                                                                                                 
 options: "4.0"                                                                                                                 
 options: "1000.0"
}

variable {
 name: "q"
 type: ENUM
 size: 1
 options: "0.5"                                                                                                                  
 options: "1.0"                                                                                                                  
 options: "2.0"                                                                                                                  
 options: "0.25"                                                                                                                 
 options: "4.0"                                                                                                                 
 options: "1000.0"
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

variable {
 name: "directed"
 type: ENUM
 size: 1
 options: "True"
 options: "False"
}

variable {
 name: "weighted"
 type: ENUM
 size: 1
 options: "True"
 options: "False"
}