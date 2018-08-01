package main

// Constant declarations
const TOO_HIGH = 1
const TOO_LOW = -1
const CORRECT = 0


func play(n int, guess func(n int) int) int {
    min, max, mid := 1, n, (1 + n) / 2 
    for {
        if min == max {
            return min 
        }

        mid = (min + max) / 2
        switch guess(mid) {
        case TOO_HIGH:
            max = mid - 1
        case TOO_LOW:
            min = mid + 1
        default:
            return mid 
        }
    }
}
