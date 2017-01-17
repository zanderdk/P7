language: PYTHON
name: "test-runner"

variable {
 name: "p"
 type: ENUM
 size: 1
 options: 0.0001
 options: 0.1
 options: 1
 options: 10
 options: 1000000
}

variable {
 name: "q"
 type: ENUM
 size: 1
 options: 0.0001
 options: 0.1
 options: 1
 options: 10
 options: 1000000
}

variable {
 name: "d"
 type: ENUM
 size: 1
 options: 32
 options: 64
 options: 128
 options: 256
}

variable {
 name: "r"
 type: INT
 size: 1
 min: 2
 max: 2
}

variable {
 name: "k"
 type: INT
 size: 1
 min: 5
 max: 20
}

variable {
 name: "l"
 type: INT
 size: 1
 min: 80
 max: 80
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
# options: "divide"
 options: "stack"
# options: "hadamard"
}