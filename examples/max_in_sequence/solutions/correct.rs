pub fn max_index(n: i64, a: Vec<i64>) -> i64 {
    let mut max: i64 = 0;
    for i in 0..n {
        if a[i as usize] > a[max as usize] {
            max = i;
        }
    }
    return max;
}
