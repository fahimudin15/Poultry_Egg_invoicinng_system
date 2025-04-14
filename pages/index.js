
import Head from 'next/head';
import EggOrder from '../components/EggOrder';

function Home() {
  return (
    <div>
      <Head>
        <title>Egg Management System</title>
      </Head>
      <h1>Egg Management System</h1>
      <EggOrder />
    </div>
  );
}

export default Home;