import java.util.Scanner;

class easy1 {
	public static void main(String args[]) {
		Scanner s = new Scanner(System.in);
		int N, max = 0;
    		N = s.nextInt();
   		for (int i=0; i<N; i++) {
        		int x = s.nextInt();
        		if (i == 0 || x > max)
            			max = x;
    		}
    		System.out.println(max);
	}
}
