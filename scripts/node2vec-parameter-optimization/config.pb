language: PYTHON
name: "test-runner"

variable {
 name: "p"
 type: FLOAT
 size: 1
 min:  0.5
 max:  0.5
}

variable {
 name: "q"
 type: FLOAT
 size: 1
 min:  100000.0
 max:  100000.0
}

variable {
 name: "d"
 type: INT
 size: 1
 min: 256
 max: 256
# options: "64"
 #options: "128"
}

variable {
 name: "r"
 type: ENUM
 size: 1
 options: "2"
}

variable {
 name: "k"
 type: INT
 size: 1
 min: 120
 max: 120
# options: "5"
# options: "10"
# options: "20"
# options: "30"
}

variable {
 name: "l"
 type: INT
 size: 1
 min: 800
 max: 800
 #options: "80"
 #options: "120"
}

variable {
 name: "directed"
 type: ENUM
 size: 1
 options: "True"
}

variable {
 name: "function"
 type: ENUM
 size: 1
 options: "divide"
 options: "stack"
 options: "hadamard"
}