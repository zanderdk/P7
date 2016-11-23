language: PYTHON
name: "test-runner"

variable {
 name: "p"
 type: ENUM
 size: 1
 options: "0.0001"
 options: "0.25"
 options: "0.50"
 options: "1.0"
 options: "2.0"
 options: "4.0"
 options: "100000.0"
 options: "1000000.0"
}

variable {
 name: "q"
 type: ENUM
 size: 1
 options: "0.0001"
 options: "0.25"
 options: "0.50"
 options: "1.0"
 options: "2.0"
 options: "4.0"
 options: "100000.0"
 options: "1000000.0"
}

variable {
 name: "d"
 type: INT
 size: 1
 min: 64
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
 min: 10
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
 min: 80
 max: 80
 #options: "80"
 #options: "120"
}

variable {
 name: "directed"
 type: ENUM
 size: 1
 options: "True"
}
