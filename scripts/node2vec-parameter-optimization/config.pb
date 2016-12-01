language: PYTHON
name: "test-runner"

variable {
 name: "p"
 type: FLOAT
 size: 1
 min:  0.0000001
 max:  1000000.0
}

variable {
 name: "q"
 type: FLOAT
 size: 1
 min:  0.0000001
 max:  1000000.0
}

variable {
 name: "d"
 type: INT
 size: 1
 min: 32
 max: 256
}

variable {
 name: "r"
 type: INT
 size: 1
 min: 1
 max: 1
}

variable {
 name: "k"
 type: INT
 size: 1
 min: 40
 max: 120
}

variable {
 name: "l"
 type: INT
 size: 1
 min: 60
 max: 200
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